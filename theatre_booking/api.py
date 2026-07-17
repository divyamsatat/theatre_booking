# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _


# ----------------------------------------------------------------
# READ-ONLY PUBLIC APIs (allow_guest=True — no login needed)
# ----------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def get_movies():
	"""
	Returns all movies that have at least one Active show.
	Used by the Movies listing page.
	"""
	movies = frappe.db.sql("""
		SELECT DISTINCT
			m.name, m.movie_name, m.duration, m.language, m.genre
		FROM `tabMovie` m
		INNER JOIN `tabShow` s ON s.movie = m.name
		WHERE s.status = 'Active'
		ORDER BY m.movie_name
	""", as_dict=True)

	for movie in movies:
		movie.show_count = frappe.db.count(
			"Show", {"movie": movie.name, "status": "Active"}
		)

	return movies


@frappe.whitelist(allow_guest=True)
def get_shows_for_movie(movie: str):
	"""
	Returns all Active shows for a given movie with seat availability.
	Used by the Shows selection page.
	"""
	shows = frappe.db.sql("""
		SELECT
			s.name, s.show_date, s.show_time,
			s.theatre, s.screen,
			s.regular_seat_price, s.premium_seat_price,
			t.location
		FROM `tabShow` s
		LEFT JOIN `tabTheatre` t ON t.name = s.theatre
		WHERE s.movie = %(movie)s AND s.status = 'Active'
		ORDER BY s.show_date, s.show_time
	""", {"movie": movie}, as_dict=True)

	for show in shows:
		avail = _get_availability(show.name)
		show.regular_available = avail["regular_available"]
		show.premium_available = avail["premium_available"]
		show.total_regular = avail["total_regular"]
		show.total_premium = avail["total_premium"]

	return shows


@frappe.whitelist(allow_guest=True)
def get_seat_availability(show: str):
	"""
	Returns remaining Regular + Premium seat counts for a show.
	Used by the booking modal to refresh availability.
	"""
	return _get_availability(show)


def _get_availability(show_name):
	"""Internal helper — computes seat availability for a show."""
	show_doc = frappe.get_doc("Show", show_name)
	screen = frappe.get_doc("Screen", show_doc.screen)

	total_regular = sum(1 for s in screen.seats if s.seat_type == "Regular")
	total_premium = sum(1 for s in screen.seats if s.seat_type == "Premium")

	booked_regular = frappe.db.sql("""
		SELECT COALESCE(SUM(num_seats), 0)
		FROM `tabBooking`
		WHERE `show` = %s AND seat_type = 'Regular' AND status = 'Confirmed'
	""", show_name)[0][0] or 0

	booked_premium = frappe.db.sql("""
		SELECT COALESCE(SUM(num_seats), 0)
		FROM `tabBooking`
		WHERE `show` = %s AND seat_type = 'Premium' AND status = 'Confirmed'
	""", show_name)[0][0] or 0

	return {
		"total_regular": total_regular,
		"total_premium": total_premium,
		"regular_available": max(0, total_regular - booked_regular),
		"premium_available": max(0, total_premium - booked_premium),
		"regular_price": show_doc.regular_seat_price,
		"premium_price": show_doc.premium_seat_price,
	}


# ----------------------------------------------------------------
# BOOKING MUTATION (allow_guest=True — customer doesn't need login)
# ----------------------------------------------------------------

@frappe.whitelist(allow_guest=True)
def create_booking(show: str, customer_name: str, num_seats: int, seat_type: str,
				   customer_email: str = "", customer_phone: str = ""):
	"""
	Creates a Booking from the public booking modal.
	Returns the new Booking name on success.
	"""
	if not frappe.db.exists("Show", show):
		frappe.throw(_("Show {0} does not exist.").format(show))

	booking = frappe.get_doc({
		"doctype": "Booking",
		"show": show,
		"customer_name": customer_name,
		"customer_email": customer_email or "",
		"customer_phone": customer_phone or "",
		"seat_type": seat_type,
		"num_seats": int(num_seats),
	})

	booking.insert(ignore_permissions=True)

	# Fetch keys and create Razorpay Order
	settings_name = frappe.db.get_value("Theater Booking Settings", filters={}, fieldname="name")
	if not settings_name:
		frappe.throw(_("Payment gateway is not configured on the server."))
	settings = frappe.get_doc("Theater Booking Settings", settings_name)
	
	if not settings.razorpay_key_id or not settings.razorpay_key_secret:
		frappe.throw(_("Payment gateway is not configured on the server."))

	import razorpay
	client = razorpay.Client(auth=(settings.razorpay_key_id, settings.get_password("razorpay_key_secret")))
	
	amount_in_paise = int(booking.total_amount * 100)
	
	order = client.order.create({
		"amount": amount_in_paise,
		"currency": "INR",
		"receipt": booking.name
	})

	# Save the order ID back to the booking
	booking.db_set("razorpay_order_id", order["id"])
	frappe.db.commit()

	return {
		"booking_id": booking.name,
		"razorpay_order_id": order["id"],
		"amount": amount_in_paise,
		"key_id": settings.razorpay_key_id,
		"customer_name": booking.customer_name,
		"customer_email": booking.customer_email,
		"customer_phone": booking.customer_phone
	}


@frappe.whitelist(allow_guest=True)
def verify_payment(razorpay_payment_id: str, razorpay_order_id: str, razorpay_signature: str, booking_name: str):
	settings_name = frappe.db.get_value("Theater Booking Settings", filters={}, fieldname="name")
	settings = frappe.get_doc("Theater Booking Settings", settings_name)
	import razorpay
	client = razorpay.Client(auth=(settings.razorpay_key_id, settings.get_password("razorpay_key_secret")))
	
	try:
		client.utility.verify_payment_signature({
			'razorpay_order_id': razorpay_order_id,
			'razorpay_payment_id': razorpay_payment_id,
			'razorpay_signature': razorpay_signature
		})
	except Exception as e:
		frappe.throw(_("Payment verification failed: {0}").format(str(e)))

	booking = frappe.get_doc("Booking", booking_name)
	if booking.razorpay_order_id != razorpay_order_id:
		frappe.throw(_("Order ID mismatch for this booking."))

	# Successfully paid -> Confirm booking
	booking.status = "Confirmed"
	booking.save(ignore_permissions=True)
	frappe.db.commit()

	return booking.name


@frappe.whitelist(allow_guest=True)
def razorpay_webhook():
	"""
	Webhook endpoint for Razorpay.
	Receives events like payment.captured and order.paid.
	"""
	raw_body = frappe.request.get_data()
	signature = frappe.request.headers.get("X-Razorpay-Signature")

	if not signature:
		frappe.throw(_("Missing Razorpay signature"), exc=frappe.PermissionError)

	settings_name = frappe.db.get_value("Theater Booking Settings", filters={}, fieldname="name")
	settings = frappe.get_doc("Theater Booking Settings", settings_name)
	if not settings.razorpay_webhook_secret:
		frappe.throw(_("Webhook secret is not configured"))

	import razorpay
	import json
	client = razorpay.Client(auth=(settings.razorpay_key_id, settings.get_password("razorpay_key_secret")))

	try:
		webhook_secret = settings.get_password("razorpay_webhook_secret")
		client.utility.verify_webhook_signature(
			raw_body.decode('utf-8') if isinstance(raw_body, bytes) else raw_body, 
			signature, 
			webhook_secret
		)
	except Exception as e:
		frappe.throw(_("Webhook signature verification failed: {0}").format(str(e)), exc=frappe.PermissionError)

	# Signature is valid. Parse payload
	payload = json.loads(raw_body)
	event = payload.get("event")

	if event in ["payment.captured", "order.paid"]:
		# Get Razorpay order ID from payload
		if event == "payment.captured":
			payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
			rzp_order_id = payment_entity.get("order_id")
		else:
			order_entity = payload.get("payload", {}).get("order", {}).get("entity", {})
			rzp_order_id = order_entity.get("id")

		if not rzp_order_id:
			return "OK"  # No order ID to process

		# Find the corresponding Booking
		booking_name = frappe.db.get_value("Booking", {"razorpay_order_id": rzp_order_id}, "name")
		if booking_name:
			booking = frappe.get_doc("Booking", booking_name)
			if booking.status != "Confirmed":
				booking.status = "Confirmed"
				booking.save(ignore_permissions=True)
				frappe.db.commit()

	return "OK"


# ----------------------------------------------------------------
# ADMIN APIs (require login)
# ----------------------------------------------------------------

@frappe.whitelist()
def cancel_show(show_name: str):
	"""
	Cancels a Show and bulk-cancels all its Confirmed bookings.
	"""
	show = frappe.get_doc("Show", show_name)

	if show.status == "Cancelled":
		frappe.throw(_("This show is already cancelled."))

	confirmed_bookings = frappe.get_all(
		"Booking",
		filters={"show": show_name, "status": "Confirmed"},
		fields=["name"],
	)

	for b in confirmed_bookings:
		frappe.db.set_value("Booking", b.name, "status", "Cancelled")

	show.status = "Cancelled"
	show.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"cancelled_bookings": len(confirmed_bookings),
		"show": show_name,
	}
