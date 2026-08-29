import re

import frappe
from frappe.model.document import Document
from frappe.utils import today

from neer_jal.neer_jal.utils import validate_phone_number

PINCODE_PATTERN = re.compile(r"^\d{6}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_EMPLOYEE_CODE = 999


class Employee(Document):
	def before_insert(self):
		if not self.joining_date:
			self.joining_date = today()
		if not self.employee_code:
			last_code = frappe.db.sql(
				"select max(cast(employee_code as unsigned)) from `tabEmployee` "
				"where employee_code regexp '^[0-9]+$'"
			)[0][0]
			next_code = (int(last_code) if last_code else 0) + 1
			if next_code > MAX_EMPLOYEE_CODE:
				frappe.throw(f"Maximum of {MAX_EMPLOYEE_CODE} employees (3-digit ID limit) reached")
			self.employee_code = f"{next_code:03d}"

	def validate(self):
		if self.phone:
			self.phone = validate_phone_number(self.phone, "Phone")
		if self.pincode and not PINCODE_PATTERN.match(self.pincode):
			frappe.throw("Pincode must be exactly 6 digits")
		if self.email and not EMAIL_PATTERN.match(self.email):
			frappe.throw("Enter a valid email address")
