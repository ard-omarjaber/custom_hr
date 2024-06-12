# encoding=utf8
# -*- coding: utf-8 -*- u
from __future__ import unicode_literals
from __future__ import division
import frappe
import frappe, os , math
from frappe import _, msgprint
from frappe.model.document import Document
from frappe.utils import get_site_base_path, cint, comma_and, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_first_day, add_years, add_months, add_days, nowdate, now_datetime, get_datetime, get_datetime, time_diff_in_hours, get_last_day, get_first_day
from frappe.utils.data import flt, nowdate, getdate, cint, rounded, add_months, add_days, get_last_day
import datetime
from datetime import date
from hrms.hr.doctype.leave_control_panel.leave_control_panel import LeaveControlPanel
from hrms.hr.doctype.leave_policy_assignment.leave_policy_assignment import LeavePolicyAssignment

# customize leave allocation creation to execlude some leave type condition
class CustomLeaveControlPanel(LeaveControlPanel):
    @frappe.whitelist()
    def allocate_leave(self):
        self.validate_values()
        leave_allocated_for = []
        employees = self.get_employees()
        if not employees:
            frappe.throw(_("No employee found"))

        for d in self.get_employees():
            
            employee_gender = frappe.db.get_value("Employee", cstr(d[0]), "gender")
            employee_marital_status= frappe.db.get_value("Employee", cstr(d[0]), "marital_status")
            female_only = frappe.db.get_value("Leave Type", self.leave_type, "custom_female_only")

            one_time_use = frappe.db.get_value("Leave Type", self.leave_type, "custom_one_time_use")

            try:
                if female_only and (employee_marital_status!='Married' or employee_gender!='Female'):
                    pass
                elif frappe.db.exists("Leave Application", {"employee": cstr(d[0]), "leave_type": self.leave_type, "docstatus": 1, "status": 'Approved'}):
                    pass
                else:
                    la = frappe.new_doc("Leave Allocation")
                    la.set("__islocal", 1)
                    la.employee = cstr(d[0])
                    la.employee_name = frappe.db.get_value("Employee", cstr(d[0]), "employee_name")
                    la.leave_type = self.leave_type
                    la.from_date = self.from_date
                    la.to_date = self.to_date
                    la.carry_forward = cint(self.carry_forward)
                    la.new_leaves_allocated = flt(self.no_of_days)
                    la.docstatus = 1
                    la.save()
                    leave_allocated_for.append(d[0])


                    annual_leave_type = frappe.get_value("Leave Type", filters = {"custom_is_annual_leave": 1}, fieldname = "name") or None
                    if annual_leave_type and self.leave_type==annual_leave_type:
                        leave_control_employee_child = frappe.get_doc("Leave Settings")

                        child_table = leave_control_employee_child.get('leave_control_employee_tab')
                        for item in child_table:
                            if item.employee == cstr(d[0]):
                                child_table.remove(item)

                        if flt(self.no_of_days) < 40:
                            leave_control_employee_child.append('leave_control_employee_tab', {
                                "employee": cstr(d[0]),
                                "leave_allocation": la.name
                            })
                            leave_control_employee_child.save()

            except Exception:
                pass
        if leave_allocated_for:
            msgprint(_("Leaves Allocated Successfully for {0}").format(comma_and(leave_allocated_for)))


    def validate_values(self):
        for f in ["from_date", "to_date", "leave_type", "no_of_days"]:
            if not self.get(f):
                frappe.throw(_("{0} is required").format(self.meta.get_label(f)))
        self.validate_from_to_dates("from_date", "to_date")





# customize leave allocation creation to execlude some leave type condition
class CustomLeavePolicyAssignment(LeavePolicyAssignment):
    def on_submit(self):
        self.grant_leave_alloc_for_employee()

    def grant_leave_alloc_for_employee(self):
        if self.leaves_allocated:
            frappe.throw(_("Leave already have been assigned for this Leave Policy Assignment"))
        else:
            leave_allocations = {}
            leave_type_details = get_leave_type_details()

            leave_policy = frappe.get_doc("Leave Policy", self.leave_policy)
            date_of_joining = frappe.db.get_value("Employee", self.employee, "date_of_joining")

            for leave_policy_detail in leave_policy.leave_policy_details:
                leave_details = leave_type_details.get(leave_policy_detail.leave_type)

                employee_gender = frappe.db.get_value("Employee", self.employee, "gender")
                employee_marital_status= frappe.db.get_value("Employee", self.employee, "marital_status")
                female_only = frappe.db.get_value("Leave Type", leave_details.name, "custom_female_only")
                one_time_use = frappe.db.get_value("Leave Type", leave_details.name, "custom_one_time_use")

                if female_only and (employee_marital_status!='Married' or employee_gender!='Female'):
                    pass
                elif frappe.db.exists("Leave Application", {"employee": self.employee, "leave_type": leave_details.name, "docstatus": 1, "status": 'Approved'}):
                    pass
                else:
                    if not leave_details.is_lwp:
                        leave_allocation, new_leaves_allocated = self.create_leave_allocation(
                            leave_policy_detail.annual_allocation,
                            leave_details,
                            date_of_joining,
                        )
                        leave_allocations[leave_details.name] = {
                            "name": leave_allocation,
                            "leaves": new_leaves_allocated,
                        }
            self.db_set("leaves_allocated", 1)
            return leave_allocations

    def create_leave_allocation(self, annual_allocation, leave_details, date_of_joining):
        # Creates leave allocation for the given employee in the provided leave period
        carry_forward = self.carry_forward
        if self.carry_forward and not leave_details.is_carry_forward:
            carry_forward = 0

        new_leaves_allocated = self.get_new_leaves(annual_allocation, leave_details, date_of_joining)


        employee_gender = frappe.db.get_value("Employee", self.employee, "gender")
        employee_marital_status= frappe.db.get_value("Employee", self.employee, "marital_status")
        female_only = frappe.db.get_value("Leave Type", leave_details.name, "custom_female_only")

        one_time_use = frappe.db.get_value("Leave Type", leave_details.name, "custom_one_time_use")

        try:
            if female_only and (employee_marital_status!='Married' or employee_gender!='Female'):
                pass
            elif frappe.db.exists("Leave Application", {"employee": self.employee, "leave_type": leave_details.name, "docstatus": 1, "status": 'Approved'}):
                pass
            else:
                allocation = frappe.get_doc(
                    dict(
                        doctype="Leave Allocation",
                        employee=self.employee,
                        leave_type=leave_details.name,
                        from_date=self.effective_from,
                        to_date=self.effective_to,
                        new_leaves_allocated=new_leaves_allocated,
                        leave_period=self.leave_period if self.assignment_based_on == "Leave Policy" else "",
                        leave_policy_assignment=self.name,
                        leave_policy=self.leave_policy,
                        carry_forward=carry_forward,
                    )
                )
                allocation.save(ignore_permissions=True)
                allocation.submit()

                annual_leave_type = frappe.get_value("Leave Type", filters = {"custom_is_annual_leave": 1}, fieldname = "name") or None
                if annual_leave_type and leave_details.name==annual_leave_type:
                    leave_control_employee_child = frappe.get_doc("Leave Settings")

                    child_table = leave_control_employee_child.get('leave_control_employee_tab')
                    for item in child_table:
                        if item.employee == self.employee:
                            child_table.remove(item)

                    if flt(new_leaves_allocated) < 40:
                        leave_control_employee_child.append('leave_control_employee_tab', {
                            "employee": self.employee,
                            "leave_allocation": allocation.name
                        })
                        leave_control_employee_child.save()


                return allocation.name, new_leaves_allocated
        except Exception:
            pass


def get_leave_type_details():
    leave_type_details = frappe._dict()
    leave_types = frappe.get_all(
        "Leave Type",
        fields=[
            "name",
            "is_lwp",
            "is_earned_leave",
            "is_compensatory",
            "allocate_on_day",
            "is_carry_forward",
            "expire_carry_forwarded_leaves_after_days",
            "earned_leave_frequency",
            "rounding",
        ],
    )
    for d in leave_types:
        leave_type_details.setdefault(d.name, d)
    return leave_type_details





# filter leave type field to show just the allowed for employee so he can apply to
@frappe.whitelist()
def get_leave_type(doctype, txt, searchfield, start, page_len, filters):
    employee_id = filters.get('employee_id')
    ignored_leaves_type = ['']

    employee_gender = frappe.db.get_value("Employee", employee_id, "gender")
    employee_marital_status= frappe.db.get_value("Employee", employee_id, "marital_status")

    leave_types = frappe.get_all("Leave Type", filters={}, fields=["*"])
    for leave_type in leave_types:
        if leave_type.custom_female_only and (employee_marital_status!='Married' or employee_gender!='Female'):
            if leave_type.name not in ignored_leaves_type:
                ignored_leaves_type.append(leave_type.name)
        
        if frappe.db.exists("Leave Application", {"employee": employee_id, "leave_type": leave_type.name, "docstatus": 1, "status": 'Approved'}):
            if leave_type.name not in ignored_leaves_type:
                ignored_leaves_type.append(leave_type.name)

    modified_string = ','.join(["'{0}'".format(lt) for lt in ignored_leaves_type])

    return frappe.db.sql("""select name from `tabLeave Type`
        where name not in ({ignored_leaves_type})
        order by
            if(locate(%(_txt)s, name), locate(%(_txt)s, name), 99999),
            idx desc,
            name
        limit %(start)s, %(page_len)s""".format(**{
            'ignored_leaves_type': modified_string
        }), {
            'txt': "%s%%" % txt,
            '_txt': txt.replace("%", ""),
            'start': start,
            'page_len': page_len
        })







# This script will work daily to check if the date today is 25 then check the child table in the leave settings doctype which has a list of employees who are lower than 50 years and experience years is less than 20 for example and compensate the leave balance difference.
def check_update_leave_balance():
    # if getdate(nowdate()).day == 25:
    if 1==1:

        leave_control_employee_child = frappe.get_doc("Leave Settings")

        child_table = leave_control_employee_child.get('leave_control_employee_tab')
        for item in list(child_table):
            if not frappe.db.exists("Leave Allocation", {"name": item.leave_allocation, "docstatus": 1}):
                child_table.remove(item);
            else:
                emp = frappe.get_doc("Employee", item.employee)
                leave_allocation = frappe.get_doc('Leave Allocation', item.leave_allocation)
                
                employee_experience = emp.custom_total_experience
                experience_age = frappe.db.get_value("Leave Settings", "Leave Settings", "experience_age")
                experience_years = frappe.db.get_value("Leave Settings", "Leave Settings", "experience_years")

                if int(get_age(emp.date_of_birth))>=int(experience_age) or int(employee_experience)>int(experience_years):
                    updated_monthe_number = (getdate(leave_allocation.to_date).month-getdate(nowdate()).month)+1
                    extra_balance = 1.25
                    total_extra_balance = updated_monthe_number*extra_balance
                    
                    leave_balance = leave_allocation.new_leaves_allocated + total_extra_balance
                    leave_allocation.new_leaves_allocated = leave_balance
                    leave_allocation.save()

                    child_table.remove(item);
                    print("Increase leave balance for employee: {0}".format(emp.employee_name))

        leave_control_employee_child.save()


# Get age if inserted date
def get_age(dob):
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))




