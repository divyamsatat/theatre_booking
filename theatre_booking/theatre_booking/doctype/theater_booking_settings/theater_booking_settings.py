# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class TheaterBookingSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		razorpay_key_id: DF.Data
		razorpay_key_secret: DF.Password
		razorpay_webhook_secret: DF.Password | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Theater Booking Settings"
