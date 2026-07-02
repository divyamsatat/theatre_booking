# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Show(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		movie: DF.Link
		screen: DF.Link
		show_date: DF.Date
		show_time: DF.Time
		theatre: DF.Link
	# end: auto-generated types

	_DOCTYPE_NAME = "Show"
