// Copyright (c) 2024, Omar Jaber and contributors
// For license information, please see license.txt

frappe.ui.form.on('Group Leave Allocation', {
	leave_type(frm){
		is_annual_leave = frappe.db.get_value('Leave Type', frm.doc.leave_type, 'custom_is_annual_leave')
		frm.set_value('is_annual_leave',is_annual_leave);
		frm.refresh_field('is_annual_leave');


	},
	is_annual_leave(frm) {
		if(frm.doc.is_annual_leave == 1){
			frappe.call({
				method :"fech_defulte_days",
				doc:frm.doc,
				args: {
				},
				callback:function(r){
					if(r.message){
						console.log(r.message);
						frm.set_value('category_1', r.message.category_1);
						frm.set_value('category_2', r.message.category_2);
						frm.refresh_field('category_1');
						frm.refresh_field('category_2');
					}
				}
			});
		}

	},
	fetch_employee(frm){
		frm.set_value('employee', []);
		frm.refresh_field('employee');
		frappe.call({
			method :"get_emp_list",
			doc:frm.doc,
			args: {
				"category_1": frm.doc.category_1,
				"category_2": frm.doc.category_2,
				
			},
			callback:function(r){
				if(r.message){
					console.log(r.message);
					frm.refresh_field('employee');
				}
			}
		});
	},
});
