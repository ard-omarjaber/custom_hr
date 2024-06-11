# encoding=utf8
# -*- coding: utf-8 -*- u
from __future__ import unicode_literals
from __future__ import division
import frappe
import frappe, os , math
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_site_base_path, cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_first_day, add_years, add_months, add_days, nowdate, now_datetime, get_datetime, get_datetime, time_diff_in_hours, get_last_day, get_first_day
from frappe.utils.data import flt, nowdate, getdate, cint, rounded, add_months, add_days, get_last_day
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta



# def leave_allocation_builder_annual():
#     count = 0
#     employees = frappe.get_all("Employee", filters={"status": "Active"}, fields=["*"])
#     for employee in employees:
        
#         leave_allocation=frappe.db.sql("select from_date,to_date from `tabLeave Allocation` where employee='{0}' and docstatus=1 and leave_type='Annual Leave' order by creation desc ".format(employee.name))
#         if leave_allocation:

#             if getdate(nowdate()) > getdate(leave_allocation[0][1]):
#                 next_first_allocation = add_days(leave_allocation[0][1], 1)
#                 next_second_allocation = add_days(add_years(leave_allocation[0][1], 10), -1)
                
#                 # Get last leaves allocated balance and add it to the new one
#                 frappe.get_doc({
#                     "doctype":"Leave Allocation",
#                     "employee": employee.name,
#                     "leave_type": 'Annual Leave',
#                     "from_date": next_first_allocation,
#                     "to_date": next_second_allocation,
#                     "carry_forward": 1,
#                     "new_leaves_allocated": 1.5,
#                     "docstatus": 1
#                 }).insert(ignore_permissions=True)

#                 print(str(employee.name)+' ** '+str(next_first_allocation)+' ** '+str(next_second_allocation))
#                 count+=1

#         else:
#             year = str(getdate(nowdate()).year)
#             first_allocation = getdate(year + "-01-01")

#             next_first_allocation = getdate(first_allocation)
#             next_second_allocation = add_days(add_years(first_allocation, 10), -1)

#             if getdate(nowdate()) >= getdate(next_first_allocation):

#                 # add daily balance in new_leaves_allocated
#                 frappe.get_doc({
#                     "doctype":"Leave Allocation",
#                     "employee": employee.name,
#                     "leave_type": 'Annual Leave',
#                     "from_date": next_first_allocation,
#                     "to_date": next_second_allocation,
#                     "carry_forward": 1,
#                     "new_leaves_allocated": 1.5,
#                     "docstatus": 1
#                 }).insert(ignore_permissions=True)

#                 print(str(employee.name)+' ** '+str(next_first_allocation)+' ** '+str(next_second_allocation))
#                 count+=1


#     print('Count: ', count)





def add_new_employee_action(doc, method):
    pass




def increase_monthly_leave_balance():
    emps = frappe.get_all("Employee", filters={"status": "Active"}, fields=["*"])
    for emp in emps:
        leave_allocation = frappe.db.sql("select name from `tabLeave Allocation` where leave_type='Annual Leave' and employee='{0}' and docstatus=1 and '{1}' between from_date and to_date order by to_date desc limit 1".format(emp.name, nowdate()))
        if leave_allocation:
            doc = frappe.get_doc('Leave Allocation', leave_allocation[0][0])
            retirement_age = frappe.db.get_value("HR Settings", "HR Settings", "retirement_age")

            daily_balance = 2.5
            if retirement_age and get_age(emp.date_of_birth) >= int(retirement_age):
                daily_balance = 3.75

            leave_balance = doc.new_leaves_allocated + daily_balance
            doc.new_leaves_allocated = leave_balance
            doc.save()
            print("Increase monthly leave balance for employee: {0}".format(emp.name))



def get_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))




