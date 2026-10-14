import frappe
from frappe import _
from frappe.utils import cint, format_date, get_link_to_form, getdate

from erpnext.accounts.doctype.purchase_invoice.purchase_invoice import PurchaseInvoice


def is_po_date_validation_enabled():
	# Settings never saved -> fall back to the field default (1)
	values = frappe.db.get_singles_dict("Claudion Add-on Settings")
	return cint(values.get("validate_po_date_with_pi_date", 1))


class CustomPurchaseInvoice(PurchaseInvoice):
	def validate_posting_date_with_po(self):
		po_list = {x.purchase_order for x in self.items if x.purchase_order}

		if not po_list:
			return

		invalid_po = []
		po_dates = frappe._dict(
			frappe.get_all(
				"Purchase Order",
				filters={"name": ["in", po_list]},
				fields=["name", "transaction_date"],
				as_list=True,
			)
		)

		for po in po_list:
			po_date = po_dates[po]
			if getdate(po_date) > getdate(self.posting_date):
				invalid_po.append((get_link_to_form("Purchase Order", po), format_date(po_date)))

		if not invalid_po:
			return

		msg = _("<p>Posting Date {0} cannot be before Purchase Order date for the following:</p><ul>").format(
			frappe.bold(format_date(self.posting_date))
		)

		for po, date in invalid_po:
			msg += f"<li>{po} ({date})</li>"
		msg += "</ul>"

		if is_po_date_validation_enabled():
			# Ticked: block the save (standard ERPNext behaviour)
			frappe.throw(msg)
		else:
			# Not ticked: only warn, allow the save
			frappe.msgprint(msg, title=_("Warning"), indicator="orange")