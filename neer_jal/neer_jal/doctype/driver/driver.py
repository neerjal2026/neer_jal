# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

from frappe.model.document import Document

from neer_jal.neer_jal.utils import validate_phone_number


class Driver(Document):
	def validate(self):
		self.phone = validate_phone_number(self.phone, "Phone")
