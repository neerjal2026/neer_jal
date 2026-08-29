# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from neer_jal.neer_jal.utils import validate_phone_number

MAX_CUSTOMER_CODE = 999


class Customer(Document):
	def validate(self):
		self.phone = validate_phone_number(self.phone, "Phone")

	def before_insert(self):
		if self.customer_code:
			return

		last_code = frappe.db.sql(
			"""
			select max(cast(customer_code as unsigned))
			from `tabCustomer`
			where customer_code regexp '^[0-9]+$'
			"""
		)[0][0]

		next_code = (int(last_code) if last_code else 0) + 1
		if next_code > MAX_CUSTOMER_CODE:
			frappe.throw(f"Maximum of {MAX_CUSTOMER_CODE} customers (3-digit ID limit) reached")

		self.customer_code = f"{next_code:03d}"
