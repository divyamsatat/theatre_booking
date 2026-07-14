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
def create_booking(show: str, customer_name: str, num_seats: int | str, seat_type: str,
				   customer_email: str | None = None, customer_phone: str | None = None):
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
	frappe.db.commit()

	return booking.name


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
