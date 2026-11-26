import frappe

from claudion_addons.supplier_payment_request.setup import create_default_workflow


def execute():
	"""Sites that already had the app: give them the starting workflow once."""
	# Do not rely on the migrate having loaded the new documents before this patch runs:
	# load them here. Child tables first, then the request itself.
	for doctype in (
		"supplier_payment_request_item",
		"supplier_payment_request_invoice",
		"supplier_payment_request",
	):
		frappe.reload_doc("supplier_payment_request", "doctype", doctype)

	create_default_workflow()
