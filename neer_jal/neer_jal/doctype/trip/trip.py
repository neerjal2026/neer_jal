# Copyright (c) 2026, Neer Jal and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint, flt, now_datetime


class Trip(Document):
	def before_insert(self):
		existing = frappe.db.get_value(
			"Trip", {"sales_person": self.sales_person, "status": "Active"}, "name"
		)
		if existing:
			frappe.throw(
				f"{self.sales_person} already has an active trip ({existing}). "
				"Please close it before starting a new one."
			)

		last_end_km = frappe.db.get_value(
			"Trip",
			{"vehicle": self.vehicle, "status": "Completed"},
			"end_km",
			order_by="end_time desc",
		)
		if last_end_km is not None and flt(self.start_km) < flt(last_end_km):
			frappe.throw(
				f"Starting KM ({self.start_km}) cannot be less than this vehicle's last "
				f"trip ending KM ({last_end_km})"
			)

	def validate(self):
		if not self.start_time:
			self.start_time = now_datetime()

		self.cans_damaged = cint(self.cans_damaged)
		not_delivered = cint(self.cans_loaded) - cint(self.cans_delivered)
		if self.cans_damaged > not_delivered:
			frappe.throw(
				f"Damaged cans ({self.cans_damaged}) cannot exceed the "
				f"{not_delivered} can(s) not yet delivered on this trip"
			)
		self.cans_remaining = not_delivered - self.cans_damaged

		if flt(self.end_km):
			if flt(self.end_km) < flt(self.start_km):
				frappe.throw("Ending KM cannot be less than Starting KM")
			self.distance_km = flt(self.end_km) - flt(self.start_km)
			if not self.end_time:
				self.end_time = now_datetime()
			self.status = "Completed"
		else:
			self.distance_km = 0
			self.end_time = None
			self.status = "Active"
