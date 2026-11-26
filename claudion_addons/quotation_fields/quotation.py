import frappe
from frappe.utils import flt


def set_sales_contributions(doc, method=None):
	"""Fill in each sales person's share of a quotation.

	ERPNext already checks the sales team (no repeats, 100% in total) on any selling document
	that has one. What it does not do for a quotation is work out the amount the shares are
	taken from, because that is part of the commission section a quotation does not have.
	So this sets that amount, then lets ERPNext redo its own sums.
	"""
	if not doc.meta.get_field("sales_team") or not doc.meta.get_field("amount_eligible_for_commission"):
		return

	doc.amount_eligible_for_commission = sum(
		flt(item.base_net_amount) for item in doc.items if _grants_commission(item.item_code)
	)
	if doc.get("sales_team"):
		doc.calculate_contribution()


def _grants_commission(item_code):
	"""Sales Order reads Grant Commission from each row; a quotation row has no such field, so read it from the item."""
	if not item_code:
		return True
	value = frappe.get_cached_value("Item", item_code, "grant_commission")
	return True if value is None else bool(value)