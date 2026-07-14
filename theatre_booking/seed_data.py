"""
Theatre Booking — Sample Data Seeder
Run with:
  bench --site mysite.local execute theatre_booking.seed_data.seed
"""

import frappe
from frappe.utils import today, add_days


def seed():
	frappe.set_user("Administrator")

	print("🌱 Seeding theatre booking sample data...")

	# ── 1. THEATRE ──────────────────────────────────────────────────
	if not frappe.db.exists("Theatre", "PVR Cinemas"):
		frappe.get_doc({
			"doctype": "Theatre",
			"theatre_name": "PVR Cinemas",
			"location": "Connaught Place, New Delhi"
		}).insert(ignore_permissions=True)
		print("  ✅ Theatre: PVR Cinemas")

	if not frappe.db.exists("Theatre", "INOX Multiplex"):
		frappe.get_doc({
			"doctype": "Theatre",
			"theatre_name": "INOX Multiplex",
			"location": "Andheri West, Mumbai"
		}).insert(ignore_permissions=True)
		print("  ✅ Theatre: INOX Multiplex")

	# ── 2. MOVIES ───────────────────────────────────────────────────
	movies = [
		{"movie_name": "Inception",     "duration": 9120,  "language": "English", "genre": "Sci-Fi"},
		{"movie_name": "KGF Chapter 3", "duration": 9900,  "language": "Hindi",   "genre": "Action"},
		{"movie_name": "Dune Part 3",   "duration": 9360,  "language": "English", "genre": "Sci-Fi"},
		{"movie_name": "Animal Park",   "duration": 8520,  "language": "Hindi",   "genre": "Action"},
		{"movie_name": "Stree 3",       "duration": 7860,  "language": "Hindi",   "genre": "Comedy"},
	]
	for m in movies:
		if not frappe.db.exists("Movie", m["movie_name"]):
			frappe.get_doc({"doctype": "Movie", **m}).insert(ignore_permissions=True)
			print(f"  ✅ Movie: {m['movie_name']}")

	# ── 3. SCREENS with seats ────────────────────────────────────────
	def make_screen(screen_name, theatre, rows):
		"""rows = list of (label, count, seat_type)"""
		if frappe.db.exists("Screen", {"screen_name": screen_name, "theatre": theatre}):
			return frappe.db.get_value("Screen", {"screen_name": screen_name, "theatre": theatre}, "name")

		seat_rows = []
		for label, count, stype in rows:
			for i in range(1, count + 1):
				seat_rows.append({
					"doctype": "Seat",
					"row": label,
					"seat_number": str(i),
					"seat_type": stype,
				})

		row_config = [
			{"doctype": "Screen Row Config", "row_label": label, "num_seats": count, "seat_type": stype}
			for label, count, stype in rows
		]

		scr = frappe.get_doc({
			"doctype": "Screen",
			"screen_name": screen_name,
			"theatre": theatre,
			"total_seats": sum(c for _, c, _ in rows),
			"row_config": row_config,
			"seats": seat_rows,
		}).insert(ignore_permissions=True)
		print(f"  ✅ Screen: {screen_name} ({theatre}) — {scr.total_seats} seats")
		return scr.name

	scr1 = make_screen("Screen 1", "PVR Cinemas",    [("A",20,"Regular"),("B",20,"Regular"),("C",15,"Premium"),("D",10,"Premium")])
	scr2 = make_screen("Screen 2", "PVR Cinemas",    [("A",25,"Regular"),("B",25,"Regular"),("C",10,"Premium")])
	scr3 = make_screen("Screen 1", "INOX Multiplex", [("A",30,"Regular"),("B",30,"Regular"),("C",20,"Premium"),("D",10,"Premium")])
	scr4 = make_screen("Screen 2", "INOX Multiplex", [("A",20,"Regular"),("B",15,"Premium")])

	# ── 4. SHOWS ─────────────────────────────────────────────────────
	shows = [
		# movie,           theatre,          screen, date,              time,       reg_price, prem_price
		("Inception",      "PVR Cinemas",    scr1,   today(),           "10:00:00", 220, 450),
		("Inception",      "PVR Cinemas",    scr1,   today(),           "14:00:00", 220, 450),
		("Inception",      "PVR Cinemas",    scr1,   today(),           "18:30:00", 250, 500),
		("Inception",      "INOX Multiplex", scr3,   today(),           "11:00:00", 200, 420),
		("KGF Chapter 3",  "PVR Cinemas",    scr2,   today(),           "09:30:00", 230, 480),
		("KGF Chapter 3",  "PVR Cinemas",    scr2,   today(),           "13:00:00", 230, 480),
		("KGF Chapter 3",  "INOX Multiplex", scr3,   add_days(today(),1),"15:00:00",210, 430),
		("Dune Part 3",    "PVR Cinemas",    scr1,   add_days(today(),1),"17:00:00",250, 520),
		("Dune Part 3",    "INOX Multiplex", scr4,   add_days(today(),1),"20:00:00",240, 500),
		("Animal Park",    "PVR Cinemas",    scr2,   add_days(today(),1),"10:30:00",200, 400),
		("Animal Park",    "INOX Multiplex", scr4,   today(),           "19:00:00", 200, 400),
		("Stree 3",        "PVR Cinemas",    scr1,   add_days(today(),2),"11:00:00",190, 380),
		("Stree 3",        "INOX Multiplex", scr3,   add_days(today(),2),"16:00:00",190, 380),
	]

	for movie, theatre, screen, date, time, reg, prem in shows:
		exists = frappe.db.exists("Show", {
			"movie": movie, "theatre": theatre, "screen": screen,
			"show_date": date, "show_time": time
		})
		if not exists:
			frappe.get_doc({
				"doctype": "Show",
				"movie": movie,
				"theatre": theatre,
				"screen": screen,
				"show_date": date,
				"show_time": time,
				"regular_seat_price": reg,
				"premium_seat_price": prem,
				"status": "Active",
			}).insert(ignore_permissions=True)
			print(f"  ✅ Show: {movie} @ {theatre} — {date} {time}")

	frappe.db.commit()
	print("\n🎉 Done! Visit http://mysite.local:8000/theatre-booking to see the movies.")
