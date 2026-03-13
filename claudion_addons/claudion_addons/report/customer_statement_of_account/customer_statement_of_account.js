// // Copyright (c) 2026, ERPGulf and contributors
// // For license information, please see license.txt

// frappe.query_reports["Customer Statement of Account"] = {
// 	"filters": [

// 	]
// };
// // Copyright (c) 2025, Erpgulf and contributors
// // For license information, please see license.txt

// frappe.query_reports["Customer Statement of Account"] = {
// 	"filters": [
// 		{
// 			"fieldname": "customer",
// 			"label": __("Customer"),
// 			"fieldtype": "Link",
// 			"options": "Customer"
// 		},
// 		{
// 			"fieldname": "from_date",
// 			"label": __("From Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
// 		},
// 		{
// 			"fieldname": "to_date",
// 			"label": __("To Date"),
// 			"fieldtype": "Date",
// 			"default": frappe.datetime.get_today()
// 		}

// 	]
// };
frappe.query_reports["Customer Statement of Account"] = {
	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "party",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			get_data: function (txt) {
				return frappe.db.get_link_options("Customer", txt, {
					company: frappe.query_report.get_filter_value("company"),
				});
			},
			on_change: function () {
				let customers = frappe.query_report.get_filter_value("party");

				// Always normalize to array
				if (!Array.isArray(customers)) {
					customers = customers ? [customers] : [];
				}

				if (customers.length === 1) {
					frappe.db.get_value("Customer", customers[0], ["customer_name", "tax_id"], function (value) {
						frappe.query_report.set_filter_value("party_name", value.customer_name);
						frappe.query_report.set_filter_value("tax_id", value.tax_id);
					});
				} else {
					frappe.query_report.set_filter_value("party_name", "");
					frappe.query_report.set_filter_value("tax_id", "");
				}
			},
		},
		{
			fieldname: "party_name",
			label: __("Customer Name"),
			fieldtype: "Data",
			hidden: 1,
		},
		{
			fieldname: "tax_id",
			label: __("Tax ID"),
			fieldtype: "Data",
			hidden: 1,
		},
		{
			fieldname: "categorize_by",
			label: __("Categorize By"),
			fieldtype: "Select",
			options: [
				"",
				{ label: __("Categorize by Voucher"), value: "Categorize by Voucher" },
				{ label: __("Categorize by Voucher (Consolidated)"), value: "Categorize by Voucher (Consolidated)" },
				{ label: __("Categorize by Account"), value: "Categorize by Account" },
			],
			default: "Categorize by Voucher (Consolidated)",
		},
		{
			fieldname: "presentation_currency",
			label: __("Currency"),
			fieldtype: "Select",
			options: erpnext.get_presentation_currency_list(),
		},
		{
			fieldname: "include_dimensions",
			label: __("Consider Accounting Dimensions"),
			fieldtype: "Check",
			default: 1,
		},
			{
			fieldname: "ignore_cr_dr_notes",
			label: __("Ignore System Generated Credit / Debit Notes"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_remarks",
			label: __("Show Remarks"),
			fieldtype: "Check",
		}
	]
};