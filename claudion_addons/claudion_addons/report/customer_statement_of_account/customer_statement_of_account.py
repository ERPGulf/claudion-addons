
# import frappe
# from frappe import _
# from frappe.utils import formatdate, escape_html
# from frappe.contacts.doctype.address.address import get_default_address
# from erpnext.accounts.report.general_ledger import general_ledger

# """
# Customer Statement of Account Report
# Based on General Ledger report filtered for Customer
# Adds:
#     - Customer Name column
#     - Remarks shown only if checkbox enabled
#     - Customer PO No and PO Date from Sales Invoice
#     - Payment Entry reference_no and reference_date
#     - Bilingual customer name / address / VAT (on first row) for the print header
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
# 	# REMOVE REMARKS COLUMN IF CHECKBOX NOT TICKED
# 	# --------------------------------------------------
# 	if not filters.get("show_remarks"):
# 		columns = [col for col in columns if col.get("fieldname") != "remarks"]

# 	# --------------------------------------------------
# 	# ADD CUSTOMER NAME COLUMN IF MISSING
# 	# --------------------------------------------------
# 	if not any(col.get("fieldname") == "party_name" for col in columns):
# 		party_index = next(
# 			(i for i, c in enumerate(columns) if c.get("fieldname") == "party"), None
# 		)
# 		if party_index is not None:
# 			columns.insert(
# 				party_index + 1,
# 				{
# 					"label": _("Customer Name"),
# 					"fieldname": "party_name",
# 					"fieldtype": "Data",
# 					"width": 150,
# 				},
# 			)

# 	# --------------------------------------------------
# 	# PREPARE LOOKUP MAPS
# 	# --------------------------------------------------
# 	customer_map = get_customer_map()
# 	po_map = get_sales_invoice_po_map(data)
# 	payment_ref_map = get_payment_entry_reference_map(data)

# 	# Get remarks length once
# 	remarks_length = None
# 	if filters.get("show_remarks"):
# 		remarks_length = frappe.get_single_value(
# 			"Accounts Settings", "general_ledger_remarks_length"
# 		)

# 	# --------------------------------------------------
# 	# ENRICH DATA
# 	# --------------------------------------------------
# 	for row in data:

# 		# Add Customer Name
# 		if row.get("party") and row.get("party_type") == "Customer":
# 			row["party_name"] = customer_map.get(row["party"], "")

# 		# Add PO Details
# 		if row.get("voucher_type") == "Sales Invoice":
# 			po = po_map.get(row.get("voucher_no"))
# 			if po:
# 				row["po_no"] = po.get("po_no")
# 				row["po_date"] = po.get("po_date")

# 		# Add Payment Entry Reference
# 		if row.get("voucher_type") == "Payment Entry":
# 			ref = payment_ref_map.get(row.get("voucher_no"))
# 			if ref:
# 				row["reference_no"] = ref.get("reference_no")
# 				row["reference_date"] = formatdate(ref.get("reference_date"))

# 		# Handle Remarks
# 		if filters.get("show_remarks"):
# 			if remarks_length and row.get("remarks"):
# 				row["remarks"] = row.get("remarks")[:remarks_length]
# 		else:
# 			row.pop("remarks", None)

# 	# --------------------------------------------------
# 	# CUSTOMER HEADER DETAILS FOR PRINT
# 	# Attached to the first row; the print format reads them from there
# 	# --------------------------------------------------
# 	if data and filters.get("party") and len(filters.party) == 1:
# 		details = get_customer_details(filters.party[0])
# 		data[0].update(
# 			{
# 				"cust_name": details.get("customer_name", ""),
# 				"cust_name_ar": details.get("customer_name_ar", ""),
# 				"cust_tax_id": details.get("tax_id", ""),
# 				"cust_address_en": details.get("address_en", ""),
# 				"cust_address_ar": details.get("address_ar", ""),
# 			}
# 		)

# 	return columns, data, None, get_report_summary(filters)


# # --------------------------------------------------
# # CUSTOMER DETAILS FOR PRINT HEADER
# # --------------------------------------------------
# def get_customer_details(customer):
# 	if not customer:
# 		return {}

# 	cust = frappe.get_doc("Customer", customer)

# 	customer_name = cust.customer_name or cust.name
# 	customer_name_ar = (
# 		cust.get("custom_customer_name_in_arabic")
# 		or cust.get("zatca_customer_name_in_arabic")
# 		or ""
# 	)

# 	address_name = cust.get("customer_primary_address") or get_default_address(
# 		"Customer", cust.name
# 	)
# 	addr = frappe.get_doc("Address", address_name) if address_name else None

# 	return {
# 		"customer_name": customer_name,
# 		"customer_name_ar": customer_name_ar,
# 		"tax_id": cust.tax_id or "",
# 		"address_en": get_address_en(addr),
# 		"address_ar": get_address_ar(addr),
# 	}


# def _building_no(a):
# 	return a.get("custom_building_number") or a.get("building_number") or ""


# def get_address_en(a):
# 	if not a:
# 		return ""

# 	building_no = _building_no(a)
# 	lines = []

# 	if a.address_line1:
# 		lines.append(escape_html(a.address_line1))
# 	if a.address_line2:
# 		lines.append(escape_html(a.address_line2))

# 	if building_no or a.city or a.pincode:
# 		city_line = ""
# 		if building_no:
# 			city_line += f"Building No. {escape_html(building_no)}, "
# 		city_line += escape_html(a.city or "")
# 		if a.pincode:
# 			city_line += f" {escape_html(a.pincode)}"
# 		lines.append(city_line.strip())

# 	if a.country:
# 		lines.append(escape_html(a.country))

# 	return "<br>".join(lines)


# def get_address_ar(a):
# 	"""Arabic fields fall back to English."""
# 	if not a:
# 		return ""

# 	building_no = _building_no(a)
# 	line1 = (
# 		a.get("custom_address_line_1_in_arabic")
# 		or a.get("address_line_1_in_arabic")
# 		or a.address_line1
# 		or ""
# 	)
# 	line2 = (
# 		a.get("custom_address_line_2_in_arabic")
# 		or a.get("address_line_2_in_arabic")
# 		or a.address_line2
# 		or ""
# 	)
# 	city = a.get("custom_city_in_arabic") or a.get("city_in_arabic") or a.city or ""
# 	country = (
# 		"المملكة العربية السعودية" if a.country == "Saudi Arabia" else (a.country or "")
# 	)

# 	lines = []
# 	if line1:
# 		lines.append(escape_html(line1))
# 	if line2:
# 		lines.append(escape_html(line2))

# 	if building_no or city or a.pincode:
# 		city_line = ""
# 		if building_no:
# 			city_line += f'رقم المبنى <span class="num">{escape_html(building_no)}</span>، '
# 		city_line += escape_html(city)
# 		if a.pincode:
# 			city_line += f' <span class="num">{escape_html(a.pincode)}</span>'
# 		lines.append(city_line.strip())

# 	if country:
# 		lines.append(escape_html(country))

# 	return "<br>".join(lines)


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


# # --------------------------------------------------
# # CUSTOMER MAP
# # --------------------------------------------------
# def get_customer_map():
# 	customers = frappe.get_all("Customer", fields=["name", "customer_name"])
# 	return {c.name: c.customer_name for c in customers}


# # --------------------------------------------------
# # SALES INVOICE PO MAP
# # --------------------------------------------------
# def get_sales_invoice_po_map(data):
# 	vouchers = [
# 		d.get("voucher_no") for d in data if d.get("voucher_type") == "Sales Invoice"
# 	]

# 	if not vouchers:
# 		return {}

# 	invoices = frappe.get_all(
# 		"Sales Invoice",
# 		filters={"name": ["in", vouchers]},
# 		fields=["name", "po_no", "po_date"],
# 	)

# 	return {inv.name: inv for inv in invoices}


# # --------------------------------------------------
# # PAYMENT ENTRY REFERENCE MAP
# # --------------------------------------------------
# def get_payment_entry_reference_map(data):
# 	vouchers = [
# 		d.get("voucher_no") for d in data if d.get("voucher_type") == "Payment Entry"
# 	]

# 	if not vouchers:
# 		return {}

# 	payments = frappe.get_all(
# 		"Payment Entry",
# 		filters={"name": ["in", vouchers]},
# 		fields=["name", "reference_no", "reference_date"],
# 	)

# 	return {p.name: p for p in payments}
import frappe
from frappe import _
from frappe.utils import formatdate, escape_html
from frappe.contacts.doctype.address.address import get_default_address
from erpnext.accounts.report.general_ledger import general_ledger

"""
Customer Statement of Account Report
Based on General Ledger report filtered for Customer
Adds:
    - Customer Name column
    - Remarks shown only if checkbox enabled
    - Customer PO No and PO Date from Sales Invoice
    - Payment Entry reference_no and reference_date
    - Bilingual customer name / address / VAT (on first row) for the print header
      (address is optional - if missing, it is simply not shown)
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
			(i for i, c in enumerate(columns) if c.get("fieldname") == "party"), None
		)
		if party_index is not None:
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
	# PREPARE LOOKUP MAPS
	# --------------------------------------------------
	customer_map = get_customer_map()
	po_map = get_sales_invoice_po_map(data)
	payment_ref_map = get_payment_entry_reference_map(data)

	# Get remarks length once
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

		# Add PO Details
		if row.get("voucher_type") == "Sales Invoice":
			po = po_map.get(row.get("voucher_no"))
			if po:
				row["po_no"] = po.get("po_no")
				row["po_date"] = po.get("po_date")

		# Add Payment Entry Reference
		if row.get("voucher_type") == "Payment Entry":
			ref = payment_ref_map.get(row.get("voucher_no"))
			if ref:
				row["reference_no"] = ref.get("reference_no")
				row["reference_date"] = formatdate(ref.get("reference_date"))

		# Handle Remarks
		if filters.get("show_remarks"):
			if remarks_length and row.get("remarks"):
				row["remarks"] = row.get("remarks")[:remarks_length]
		else:
			row.pop("remarks", None)

	# --------------------------------------------------
	# CUSTOMER HEADER DETAILS FOR PRINT
	# Attached to the first row; the print format reads them from there
	# --------------------------------------------------
	if data and filters.get("party") and len(filters.party) == 1:
		details = get_customer_details(filters.party[0])
		data[0].update(
			{
				"cust_name": details.get("customer_name", ""),
				"cust_name_ar": details.get("customer_name_ar", ""),
				"cust_tax_id": details.get("tax_id", ""),
				"cust_address_en": details.get("address_en", ""),
				"cust_address_ar": details.get("address_ar", ""),
			}
		)

	return columns, data, None, get_report_summary(filters)


# --------------------------------------------------
# CUSTOMER DETAILS FOR PRINT HEADER
# --------------------------------------------------
def get_customer_details(customer):
	if not customer or not frappe.db.exists("Customer", customer):
		return {}

	cust = frappe.get_doc("Customer", customer)

	details = {
		"customer_name": cust.customer_name or cust.name,
		"customer_name_ar": (
			cust.get("custom_customer_name_in_arabic")
			or cust.get("zatca_customer_name_in_arabic")
			or ""
		),
		"tax_id": cust.tax_id or "",
		"address_en": "",
		"address_ar": "",
	}

	# Address is optional: skip it silently if missing / deleted / unreadable
	try:
		address_name = cust.get("customer_primary_address")
		if not address_name or not frappe.db.exists("Address", address_name):
			address_name = get_default_address("Customer", cust.name)

		if address_name and frappe.db.exists("Address", address_name):
			addr = frappe.get_doc("Address", address_name)
			details["address_en"] = get_address_en(addr)
			details["address_ar"] = get_address_ar(addr)
	except Exception:
		frappe.log_error(title="Customer Statement: address lookup failed")

	return details


def _building_no(a):
	return a.get("custom_building_number") or a.get("building_number") or ""


def get_address_en(a):
	if not a:
		return ""

	building_no = _building_no(a)
	lines = []

	if a.get("address_line1"):
		lines.append(escape_html(a.address_line1))
	if a.get("address_line2"):
		lines.append(escape_html(a.address_line2))

	if building_no or a.get("city") or a.get("pincode"):
		city_line = ""
		if building_no:
			city_line += f"Building No. {escape_html(building_no)}, "
		city_line += escape_html(a.get("city") or "")
		if a.get("pincode"):
			city_line += f" {escape_html(a.pincode)}"
		lines.append(city_line.strip().rstrip(","))

	if a.get("country"):
		lines.append(escape_html(a.country))

	return "<br>".join(lines)


def get_address_ar(a):
	"""Arabic fields fall back to English."""
	if not a:
		return ""

	building_no = _building_no(a)
	line1 = (
		a.get("custom_address_line_1_in_arabic")
		or a.get("address_line_1_in_arabic")
		or a.get("address_line1")
		or ""
	)
	line2 = (
		a.get("custom_address_line_2_in_arabic")
		or a.get("address_line_2_in_arabic")
		or a.get("address_line2")
		or ""
	)
	city = a.get("custom_city_in_arabic") or a.get("city_in_arabic") or a.get("city") or ""
	country = (
		"المملكة العربية السعودية"
		if a.get("country") == "Saudi Arabia"
		else (a.get("country") or "")
	)

	lines = []
	if line1:
		lines.append(escape_html(line1))
	if line2:
		lines.append(escape_html(line2))

	if building_no or city or a.get("pincode"):
		city_line = ""
		if building_no:
			city_line += f'رقم المبنى <span class="num">{escape_html(building_no)}</span>، '
		city_line += escape_html(city)
		if a.get("pincode"):
			city_line += f' <span class="num">{escape_html(a.pincode)}</span>'
		lines.append(city_line.strip().rstrip("،"))

	if country:
		lines.append(escape_html(country))

	return "<br>".join(lines)


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
			customer_name = customer.customer_name or ""
			tax_id = customer.tax_id or ""

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
# SALES INVOICE PO MAP
# --------------------------------------------------
def get_sales_invoice_po_map(data):
	vouchers = [
		d.get("voucher_no") for d in data if d.get("voucher_type") == "Sales Invoice"
	]

	if not vouchers:
		return {}

	invoices = frappe.get_all(
		"Sales Invoice",
		filters={"name": ["in", vouchers]},
		fields=["name", "po_no", "po_date"],
	)

	return {inv.name: inv for inv in invoices}


# --------------------------------------------------
# PAYMENT ENTRY REFERENCE MAP
# --------------------------------------------------
def get_payment_entry_reference_map(data):
	vouchers = [
		d.get("voucher_no") for d in data if d.get("voucher_type") == "Payment Entry"
	]

	if not vouchers:
		return {}

	payments = frappe.get_all(
		"Payment Entry",
		filters={"name": ["in", vouchers]},
		fields=["name", "reference_no", "reference_date"],
	)

	return {p.name: p for p in payments}