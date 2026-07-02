# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Screen(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF
		from theatre_booking.theatre_booking.doctype.seat.seat import Seat

		screen_name: DF.Data
		seats: DF.Table[Seat]
		theatre: DF.Link
	# end: auto-generated types

	_DOCTYPE_NAME = "Screen"
