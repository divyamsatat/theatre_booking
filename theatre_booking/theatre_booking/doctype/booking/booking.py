# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class Booking(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		booking_date: DF.Datetime | None
		customer_email: DF.Data | None
		customer_name: DF.Data
		customer_phone: DF.Data | None
		num_seats: DF.Int
		seat_type: DF.Literal["Regular", "Premium"]
		show: DF.Link
		status: DF.Literal["Confirmed", "Cancelled"]
		total_amount: DF.Currency | None
	# end: auto-generated types

	def before_insert(self):
		"""Auto-set status to Confirmed and booking_date on new bookings."""
		self.status = "Confirmed"
		self.booking_date = now_datetime()

	def validate(self):
		"""Validate that enough seats are available for this show + seat type."""
		self._validate_num_seats()
		self._check_seat_availability()

	def before_save(self):
		"""Auto-calculate total_amount based on configurable prices on the Show."""
		self._calculate_total_amount()

	# ----------------------------------------------------------------
	# Private helpers
	# ----------------------------------------------------------------

	def _validate_num_seats(self):
		if not self.num_seats or self.num_seats < 1:
			frappe.throw(_("Number of seats must be at least 1."))

	def _calculate_total_amount(self):
		"""Fetch unit price from the linked Show and multiply by num_seats."""
		show = frappe.get_doc("Show", self.show)

		if self.seat_type == "Regular":
			unit_price = show.regular_seat_price or 0
		elif self.seat_type == "Premium":
			unit_price = show.premium_seat_price or 0
		else:
			unit_price = 0

		self.total_amount = unit_price * (self.num_seats or 0)

	def _check_seat_availability(self):
		"""
		Option A availability check:
		  Total capacity  = count of seats of this type on the linked Screen
		  Already booked  = SUM(num_seats) from Confirmed Bookings for same Show + SeatType
		  Available       = Total capacity - Already booked
		"""
		# 1. Get the screen linked to the show
		show = frappe.get_doc("Show", self.show)
		screen = frappe.get_doc("Screen", show.screen)

		# 2. Count total seats of the requested type on this screen
		total_seats_of_type = sum(
			1 for seat in screen.seats if seat.seat_type == self.seat_type
		)

		if total_seats_of_type == 0:
			frappe.throw(
				_("There are no {0} seats configured on screen {1}.").format(
					self.seat_type, show.screen
				)
			)

		# 3. Count already-confirmed bookings for this show + seat type (exclude self on edit)
		# Note: frappe.db.get_value doesn't support SQL aggregates as strings,
		# so we use frappe.db.sql with a parameterized query.
		if self.is_new():
			already_booked = frappe.db.sql(
				"""
				SELECT COALESCE(SUM(num_seats), 0)
				FROM `tabBooking`
				WHERE `show` = %s
				  AND seat_type = %s
				  AND status = 'Confirmed'
				""",
				(self.show, self.seat_type),
			)[0][0] or 0
		else:
			already_booked = frappe.db.sql(
				"""
				SELECT COALESCE(SUM(num_seats), 0)
				FROM `tabBooking`
				WHERE `show` = %s
				  AND seat_type = %s
				  AND status = 'Confirmed'
				  AND name != %s
				""",
				(self.show, self.seat_type, self.name),
			)[0][0] or 0

		available = total_seats_of_type - already_booked

		if self.num_seats > available:
			frappe.throw(
				_(
					"Not enough {seat_type} seats available for this show. "
					"Requested: {requested}, Available: {available}."
				).format(
					seat_type=self.seat_type,
					requested=self.num_seats,
					available=available,
				)
			)
