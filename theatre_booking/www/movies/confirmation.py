import frappe

no_cache = 1


def get_context(context):
	context.no_breadcrumbs = True
	context.no_header = True
	context.no_footer = True

	booking_name = frappe.form_dict.get("booking")

	booking = frappe.db.sql("""
		SELECT
			b.name, b.customer_name, b.customer_email, b.customer_phone,
			b.seat_type, b.num_seats, b.total_amount, b.status,
			b.booking_date, b.`show`, b.movie, b.theatre, b.show_date, b.show_time
		FROM `tabBooking` b
		WHERE b.name = %s
	""", booking_name, as_dict=True)

	if not booking:
		frappe.redirect_to_message("Booking Not Found", "The requested booking does not exist.")
		return

	b = booking[0]

	# Fetch show details for any missing info
	show = frappe.db.sql("""
		SELECT name, movie, theatre, show_date, show_time
		FROM `tabShow` WHERE name = %s
	""", b.show, as_dict=True)

	context.booking = b
	context.show = show[0] if show else {}
	context.title = f"Booking Confirmed — {booking_name}"
