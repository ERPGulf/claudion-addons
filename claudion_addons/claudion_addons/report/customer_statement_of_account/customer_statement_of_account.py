# # Copyright (c) 2026, ERPGulf and contributors
# # For license information, please see license.txt

# # import frappe


# def execute(filters=None):
# 	columns, data = [], []
# 	return columns, data

# import frappe
# from frappe import _
# from erpnext.accounts.report.general_ledger import general_ledger

# """
# Customer Statement of Account Report
# Based on General Ledger report filtered for Customer
# """


# def execute(filters=None):
# 	if not filters:
# 		return [], []

# 	filters = frappe._dict(filters)
# 	filters.party_type = "Customer"

# 	# Normalize party filter
# 	if filters.get("party") and not isinstance(filters.party, (list, tuple)):
# 		filters.party = [filters.party]

# 	# --------------------------------------------------
# 	# IGNORE SYSTEM GENERATED CR / DR NOTES
# 	# --------------------------------------------------
# 	if filters.get("ignore_cr_dr_notes"):
# 		system_generated_cr_dr_journals = frappe.db.get_all(
# 			"Journal Entry",
# 			filters={
# 				"company": filters.get("company"),
# 				"docstatus": 1,
# 				"voucher_type": ("in", ["Credit Note", "Debit Note"]),
# 				"is_system_generated": 1,
# 			},
# 			as_list=True,
# 		)

# 		if system_generated_cr_dr_journals:
# 			vouchers_to_ignore = (filters.get("voucher_no_not_in") or []) + [
# 				x[0] for x in system_generated_cr_dr_journals
# 			]
# 			filters.update({"voucher_no_not_in": vouchers_to_ignore})

# 	# --------------------------------------------------
# 	# GET GENERAL LEDGER DATA
# 	# --------------------------------------------------
# 	columns, data = general_ledger.execute(filters)

# 	# --------------------------------------------------
# 	# ADD CUSTOMER NAME COLUMN IF MISSING
# 	# --------------------------------------------------
# 	if not any(col.get("fieldname") == "party_name" for col in columns):
# 		party_index = next(
# 			i for i, c in enumerate(columns) if c.get("fieldname") == "party"
# 		)
# 		columns.insert(
# 			party_index + 1,
# 			{
# 				"label": _("Customer Name"),
# 				"fieldname": "party_name",
# 				"fieldtype": "Data",
# 				"width": 150,
# 			},
# 		)

# 	# --------------------------------------------------
# 	# ADD REMARKS COLUMN (ONLY IF FILTER ENABLED)
# 	# --------------------------------------------------
# 	if filters.get("show_remarks"):
# 		columns.append(
# 			{
# 				"label": _("Remarks"),
# 				"fieldname": "remarks",
# 				"fieldtype": "Data",
# 				"width": 400,
# 			}
# 		)

# 	# --------------------------------------------------
# 	# ENRICH DATA
# 	# --------------------------------------------------
# 	customer_map = get_customer_map()

# 	for row in data:
# 		if row.get("party") and row.get("party_type") == "Customer":
# 			row["party_name"] = customer_map.get(row["party"], "")

# 		# Attach remarks only if enabled
# 		if filters.get("show_remarks"):
# 			remarks_length = frappe.get_single_value(
# 				"Accounts Settings", "general_ledger_remarks_length"
# 			)

# 			if remarks_length and row.get("remarks"):
# 				row["remarks"] = row.get("remarks")[:remarks_length]

# 	return columns, data, None, get_report_summary(filters)


# # --------------------------------------------------
# # REPORT SUMMARY
# # --------------------------------------------------
# def get_report_summary(filters):
# 	customer_name, tax_id = "", ""

# 	if filters.get("party"):
# 		customer = frappe.db.get_value(
# 			"Customer",
# 			filters.party[0],
# 			["customer_name", "tax_id"],
# 			as_dict=True,
# 		)

# 		if customer:
# 			customer_name = customer.customer_name
# 			tax_id = customer.tax_id

# 	heading = "<h2 style='text-align:center;'>Statement of Account</h2>"
# 	subheading = f"""
# 	<div style='text-align:center;'>
# 	{customer_name}<br>
# 	Tax ID: {tax_id}<br>
# 	{filters.from_date} to {filters.to_date}
# 	</div>
# 	"""

# 	return [
# 		{
# 			"value": heading + subheading,
# 			"indicator": "blue",
# 			"label": "",
# 			"datatype": "HTML",
# 		}
# 	]


# # ---------------------------------- ---- ------------
# # CUSTOMER MAP
# # --------------------------------------------------
# def get_customer_map():
# 	customers = frappe.get_all("Customer", fields=["name", "customer_name"])
# 	return {c.name: c.customer_name for c in customers}
import frappe
from frappe import _
from erpnext.accounts.report.general_ledger import general_ledger

"""
Customer Statement of Account Report
Based on General Ledger report filtered for Customer
Adds:
    - Customer Name column
    - Description from Sales Invoice (custom_description_)
    - Remarks shown only if checkbox enabled
"""


def execute(filters=None):
	if not filters:
		return [], []

	filters = frappe._dict(filters)
	filters.party_type = "Customer"

	# Normalize party filter
	if filters.get("party") and not isinstance(filters.party, (list, tuple)):
		filters.party = [filters.party]

	# --------------------------------------------------
	# IGNORE SYSTEM GENERATED CR / DR NOTES
	# --------------------------------------------------
	if filters.get("ignore_cr_dr_notes"):
		system_generated_cr_dr_journals = frappe.db.get_all(
			"Journal Entry",
			filters={
				"company": filters.get("company"),
				"docstatus": 1,
				"voucher_type": ("in", ["Credit Note", "Debit Note"]),
				"is_system_generated": 1,
			},
			as_list=True,
		)

		if system_generated_cr_dr_journals:
			vouchers_to_ignore = (filters.get("voucher_no_not_in") or []) + [
				x[0] for x in system_generated_cr_dr_journals
			]
			filters.update({"voucher_no_not_in": vouchers_to_ignore})

	# --------------------------------------------------
	# GET GENERAL LEDGER DATA
	# --------------------------------------------------
	columns, data = general_ledger.execute(filters)

	# --------------------------------------------------
	# REMOVE REMARKS COLUMN IF CHECKBOX NOT TICKED
	# --------------------------------------------------
	if not filters.get("show_remarks"):
		columns = [col for col in columns if col.get("fieldname") != "remarks"]

	# --------------------------------------------------
	# ADD CUSTOMER NAME COLUMN IF MISSING
	# --------------------------------------------------
	if not any(col.get("fieldname") == "party_name" for col in columns):
		party_index = next(
			i for i, c in enumerate(columns) if c.get("fieldname") == "party"
		)
		columns.insert(
			party_index + 1,
			{
				"label": _("Customer Name"),
				"fieldname": "party_name",
				"fieldtype": "Data",
				"width": 150,
			},
		)

	# --------------------------------------------------
	# ADD DESCRIPTION COLUMN
	# --------------------------------------------------
	if not any(col.get("fieldname") == "description" for col in columns):
		columns.append(
			{
				"label": _("Description"),
				"fieldname": "description",
				"fieldtype": "Data",
				"width": 300,
			}
		)

	# --------------------------------------------------
	# PREPARE LOOKUP MAPS
	# --------------------------------------------------
	customer_map = get_customer_map()
	sales_invoice_description_map = get_sales_invoice_description_map(data)

	# Get remarks length once (performance safe)
	remarks_length = None
	if filters.get("show_remarks"):
		remarks_length = frappe.get_single_value(
			"Accounts Settings", "general_ledger_remarks_length"
		)

	# --------------------------------------------------
	# ENRICH DATA
	# --------------------------------------------------
	for row in data:

		# Add Customer Name
		if row.get("party") and row.get("party_type") == "Customer":
			row["party_name"] = customer_map.get(row["party"], "")

		# Add Description from Sales Invoice
		if row.get("voucher_type") == "Sales Invoice":
			row["description"] = sales_invoice_description_map.get(
				row.get("voucher_no"), ""
			)
		else:
			row["description"] = ""

		# Handle Remarks (only if checkbox enabled)
		if filters.get("show_remarks"):
			if remarks_length and row.get("remarks"):
				row["remarks"] = row.get("remarks")[:remarks_length]
		else:
			row.pop("remarks", None)

	return columns, data, None, get_report_summary(filters)


# --------------------------------------------------
# REPORT SUMMARY
# --------------------------------------------------
def get_report_summary(filters):
	customer_name, tax_id = "", ""

	if filters.get("party"):
		customer = frappe.db.get_value(
			"Customer",
			filters.party[0],
			["customer_name", "tax_id"],
			as_dict=True,
		)

		if customer:
			customer_name = customer.customer_name
			tax_id = customer.tax_id

	heading = "<h2 style='text-align:center;'>Statement of Account</h2>"
	subheading = f"""
	<div style='text-align:center;'>
	{customer_name}<br>
	Tax ID: {tax_id}<br>
	{filters.from_date} to {filters.to_date}
	</div>
	"""

	return [
		{
			"value": heading + subheading,
			"indicator": "blue",
			"label": "",
			"datatype": "HTML",
		}
	]


# --------------------------------------------------
# CUSTOMER MAP
# --------------------------------------------------
def get_customer_map():
	customers = frappe.get_all("Customer", fields=["name", "customer_name"])
	return {c.name: c.customer_name for c in customers}


# --------------------------------------------------
# SALES INVOICE DESCRIPTION MAP
# ---------------------------------------------- ----
def get_sales_invoice_description_map(data):
	sales_invoice_numbers = list(
		{
			row.get("voucher_no")
			for row in data
			if row.get("voucher_type") == "Sales Invoice"
			and row.get("voucher_no")
		}
	)

	if not sales_invoice_numbers:
		return {}

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"name": ("in", sales_invoice_numbers)},
		fields=["name", "custom_description_"],
	)

	return {inv.name: inv.custom_description_ for inv in invoices}