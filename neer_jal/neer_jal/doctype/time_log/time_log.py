import frappe
from frappe.model.document import Document
from frappe.utils import flt, get_datetime


class TimeLog(Document):
	def validate(self):
		if self.time_out:
			delta = get_datetime(self.time_out) - get_datetime(self.time_in)
			if delta.total_seconds() <= 0:
				frappe.throw("Time Out must be after Time In")
			self.hours = flt(delta.total_seconds() / 3600)
		else:
			self.hours = 0
