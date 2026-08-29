# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import flt

from neer_jal.neer_jal.utils import update_customer_balance


class PaymentEntry(Document):
	def validate(self):
		if flt(self.amount) <= 0:
			frappe.throw("Amount received must be greater than zero")

	def on_update(self):
		update_customer_balance(self.customer)
		previous = self.get_doc_before_save()
		if previous and previous.customer and previous.customer != self.customer:
			update_customer_balance(previous.customer)

	def after_delete(self):
		update_customer_balance(self.customer)
