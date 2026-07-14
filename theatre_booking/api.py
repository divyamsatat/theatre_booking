# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def create_booking(show, customer_name, num_seats, seat_type,
                   customer_email=None, customer_phone=None):
	"""
	Whitelisted API to create a Booking from the Show form's 'Book Seats' dialog.
	Returns the new Booking document name on success.
	"""
	# Basic guard: show must exist
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


@frappe.whitelist()
def cancel_show(show_name):
	"""
	Whitelisted API to cancel a Show and all its Confirmed bookings.
	  1. Sets show.status = 'Cancelled'
	  2. Bulk-updates all Confirmed Booking records for this show to Cancelled
	"""
	show = frappe.get_doc("Show", show_name)

	if show.status == "Cancelled":
		frappe.throw(_("This show is already cancelled."))

	# 1. Cancel all Confirmed bookings for this show
	confirmed_bookings = frappe.get_all(
		"Booking",
		filters={"show": show_name, "status": "Confirmed"},
		fields=["name"],
	)

	for b in confirmed_bookings:
		frappe.db.set_value("Booking", b.name, "status", "Cancelled")

	# 2. Set the show status to Cancelled
	show.status = "Cancelled"
	show.save(ignore_permissions=True)
	frappe.db.commit()

	return {
		"cancelled_bookings": len(confirmed_bookings),
		"show": show_name,
	}
