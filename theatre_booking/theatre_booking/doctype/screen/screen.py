# Copyright (c) 2026, Divyam Jain and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class Screen(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		screen_name: DF.Data
		theatre: DF.Link
		total_seats: DF.Int | None
	# end: auto-generated types

	def before_save(self):
		"""Keep total_seats in sync with the actual generated seats count."""
		self.total_seats = len(self.seats) if self.seats else 0
