# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class Movie(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		duration: DF.Duration
		genre: DF.Data | None
		language: DF.Data | None
		movie_name: DF.Data
	# end: auto-generated types

	_DOCTYPE_NAME = "Movie"
