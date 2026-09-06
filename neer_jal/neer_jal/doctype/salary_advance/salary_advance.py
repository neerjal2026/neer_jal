import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate, today


class SalaryAdvance(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw("Salary advance amount must be greater than zero")
		if self.advance_date and getdate(self.advance_date) > getdate(today()):
			frappe.throw("Advance date cannot be in the future")
