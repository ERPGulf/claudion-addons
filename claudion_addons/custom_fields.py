"""Fields this app adds to standard documents.

Quotation gets a Cost Center, a Project and a Sales Team. They use the same field names as
Sales Order and Sales Invoice, so ERPNext copies them across by itself when either is made
from the quotation: no mapping code is needed.
"""

from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
	"Quotation": [
		# ---- Accounting Dimensions, in the same place as on Sales Order
		{
			"fieldname": "accounting_dimensions_section",
			"fieldtype": "Section Break",
			"label": "Accounting Dimensions",
			"collapsible": 1,
			"insert_after": "amended_from",
		},
		{
			"fieldname": "cost_center",
			"fieldtype": "Link",
			"label": "Cost Center",
			"options": "Cost Center",
			"print_hide": 1,
			"insert_after": "accounting_dimensions_section",
		},
		{
			"fieldname": "dimension_col_break",
			"fieldtype": "Column Break",
			"insert_after": "cost_center",
		},
		{
			"fieldname": "project",
			"fieldtype": "Link",
			"label": "Project",
			"options": "Project",
			"print_hide": 1,
			"insert_after": "dimension_col_break",
		},
		# ---- Sales Team, at the top of the More Info tab
		{
			"fieldname": "sales_team_section",
			"fieldtype": "Section Break",
			"label": "Sales Team",
			"collapsible": 1,
			"collapsible_depends_on": "sales_team",
			"print_hide": 1,
			"insert_after": "more_info_tab",
		},
		{
			"fieldname": "sales_team",
			"fieldtype": "Table",
			"label": "Sales Team",
			"options": "Sales Team",
			"print_hide": 1,
			"insert_after": "sales_team_section",
		},
		{
			# ERPNext works out each sales person's share from this figure. Sales Order has it
			# as a visible field in its Commission section; a quotation has no commission, so
			# it is kept out of sight here.
			"fieldname": "amount_eligible_for_commission",
			"fieldtype": "Currency",
			"label": "Amount Eligible for Commission",
			"options": "Company:company:default_currency",
			"read_only": 1,
			"hidden": 1,
			"no_copy": 1,
			"print_hide": 1,
			"insert_after": "sales_team",
		},
	],
}


def setup_custom_fields():
	"""Create the fields, or bring existing ones in line. Safe to run any number of times."""
	create_custom_fields(CUSTOM_FIELDS, update=True)