# Copyright (c) 2024, Omar Jaber and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, msgprint, throw
from frappe.desk.reportview import get_filters_cond, get_match_cond

from frappe.utils import date_diff , today ,cint

# Import math library
import math


class GroupLeaveAllocation(Document):
	def validate(self):
		pass


	def on_submit(self):
		self.create_leave_allocation()	

	@frappe.whitelist()
	def fech_defulte_days(self):
		setting=  frappe.get_doc("Leave Settings")
		category_1 = setting.automatic_category_1_balance_value
		category_2= setting.automatic_category_2_balance_value
		
		return {
			"category_1" :category_1 , 
			"category_2" :category_2
			}
	
	@frappe.whitelist()
	def get_emp_list(self , category_1 , category_2 ):
		filters = make_filters(self)
		cond = get_filter_condition(filters)

		emp_list = {}
		emp_list =  frappe.db.sql(
			"""
				select
					distinct t1.name as employee, t1.employee_name, t1.department, t1.grade, t1.gender, t1.custom_office , t1.date_of_birth , t1.custom_total_experience_in_years
				from
					`tabEmployee` t1
				where
					t1.status = 'Active' 
			%s order by t1.name desc
			"""
			% cond,
			as_dict=True,
		)
		if len(emp_list) > 0:
			# for a in emp_list:
			# 	a.update({'new_leaves_allocated': self.category_1})
			new_leaves_allocated = 0.0
			setting=  frappe.get_doc("Leave Settings")

			for e in emp_list:
				e.update({'new_leaves_allocated':new_leaves_allocated})
				employee_age   = math.ceil(date_diff( today() , e.date_of_birth)/365.25)
				if (employee_age < setting.experience_age) and (cint(e.custom_total_experience_in_years ) < cint(setting.experience_years)):
					new_leaves_allocated = category_1
				else:
					new_leaves_allocated = category_2
				self.append(
					"employee",{
						"employee": e.employee,
						"employee_name": e.employee_name,
						"employee_age": employee_age,
						"total_years_of_experience": cint(e.custom_total_experience_in_years ),
						"new_leaves_allocated" :new_leaves_allocated
					}
				)
		return str(emp_list)
	def create_leave_allocation(self):
		# frappe.db.set_value("Monthly leave_allocationotion", self.name,"status", 'Approved')
		if len(self.employee) > 0:
			for e in self.employee:
					leave_allocation = frappe.new_doc("Leave Allocation")
					leave_allocation.employee = e.employee
					leave_allocation.employee_name = e.employee_name
					leave_allocation.from_date = self.from_date
					leave_allocation.to_date = self.to_date
					leave_allocation.carry_forward = self.add_unused_leaves_from_previous_allocations
					leave_allocation.leave_type = self.leave_type
					leave_allocation.new_leaves_allocated = e.new_leaves_allocated
						
					leave_allocation.save()
					frappe.db.set_value("Employee Group Leave Allocation", e.name, "employee", leave_allocation.name)
					# leave_allocation.submit()
					frappe.db.commit()

		else:
			throw(_("Employees table canot be empty."))
	
def make_filters(self):
	filters = frappe._dict()
	filters["company"] = self.company
	filters["branch"] = self.branch
	filters["department"] = self.department
	filters["custom_office"] = self.office
	filters["grade"] = self.grade
	filters["gender"] = self.gender
	return filters

def get_filter_condition(filters):
	cond = ""
	for f in ["company", "branch", "department", "custom_office" , "grade"	, "gender"]:
		if filters.get(f):
			cond += " and t1." + f + " = " + frappe.db.escape(filters.get(f))

	return cond
