import frappe

no_cache = 1


def get_context(context):
	context.no_breadcrumbs = True
	context.no_header = True
	context.no_footer = True

	movie_name = frappe.form_dict.get("movie")

	# Validate movie exists (raw SQL — avoids ORM permission check)
	movie = frappe.db.sql(
		"SELECT name, movie_name, duration, language, genre FROM `tabMovie` WHERE name = %s",
		movie_name, as_dict=True
	)
	if not movie:
		frappe.redirect_to_message("Movie Not Found", "No active shows for this movie.")
		return

	context.movie = movie[0]
	context.title = f"{movie[0].movie_name} — Shows"

	# Fetch shows with theatre location
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
	""", {"movie": movie_name}, as_dict=True)

	for show in shows:
		# Count seats from the Seat child table (raw SQL)
		seat_counts = frappe.db.sql("""
			SELECT seat_type, COUNT(*) AS total
			FROM `tabSeat`
			WHERE parent = %s
			GROUP BY seat_type
		""", show.screen, as_dict=True)

		total_regular = next((r.total for r in seat_counts if r.seat_type == "Regular"), 0)
		total_premium = next((r.total for r in seat_counts if r.seat_type == "Premium"), 0)

		booked_regular = frappe.db.sql("""
			SELECT COALESCE(SUM(num_seats), 0) FROM `tabBooking`
			WHERE `show` = %s AND seat_type = 'Regular' AND status = 'Confirmed'
		""", show.name)[0][0] or 0

		booked_premium = frappe.db.sql("""
			SELECT COALESCE(SUM(num_seats), 0) FROM `tabBooking`
			WHERE `show` = %s AND seat_type = 'Premium' AND status = 'Confirmed'
		""", show.name)[0][0] or 0

		show.total_regular = total_regular
		show.total_premium = total_premium
		show.regular_available = max(0, total_regular - booked_regular)
		show.premium_available = max(0, total_premium - booked_premium)

	context.shows = shows
