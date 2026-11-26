"""Creating draft Payment Entries from an approved Supplier Payment Request, and keeping
each request row in step with its Payment Entry afterwards.

Entries are only ever created as drafts. Submitting, editing or cancelling one is done by
the user in the standard Payment Entry form, under standard permissions.
"""

import frappe
from frappe import _
from frappe.utils import flt, get_link_to_form, getdate, today

from claudion_addons.supplier_payment_request.doctype.supplier_payment_request.supplier_payment_request import (
	AGAINST_INVOICES,
	check_invoice,
	validate_paid_from_account,
)

NOT_CREATED = "Not Created"
DRAFT_CREATED = "Draft Created"
SUBMITTED = "Submitted"

ITEM = "Supplier Payment Request Item"


@frappe.whitelist()
def create_payment_entries(request, rows, posting_date=None, paid_from_account=None):
	"""Create one draft Payment Entry for each chosen row of an approved request.

	rows: names of the item rows to process. A row that already has a Payment Entry is
	skipped, so running this twice never pays a row twice. A row that fails is reported and
	does not stop the others.
	"""
	rows = frappe.parse_json(rows) or []
	if not rows:
		frappe.throw(_("Select at least one row."))

	# Who may do this is decided by the site's permissions on Payment Entry, not by a fixed role.
	frappe.has_permission("Payment Entry", "create", throw=True)

	# Lock the request so two users pressing the button together cannot both create entries.
	doc = frappe.get_doc("Supplier Payment Request", request, for_update=True)
	doc.check_permission("read")
	if doc.docstatus != 1:
		frappe.throw(_("Payment entries can be created only after the request is approved."))

	if paid_from_account and paid_from_account != doc.paid_from_account:
		validate_paid_from_account(paid_from_account, doc.company)
		doc.db_set("paid_from_account", paid_from_account)
	posting_date = getdate(posting_date or doc.posting_date or today())
	if getdate(doc.posting_date) != posting_date:
		doc.db_set("posting_date", posting_date)

	created, failed, skipped = [], [], []

	for row in doc.items:
		if row.name not in rows:
			continue
		if row.payment_entry:
			skipped.append({"idx": row.idx, "supplier": row.supplier, "payment_entry": row.payment_entry})
			continue

		frappe.db.savepoint("spr_row")
		try:
			pe = build_payment_entry(doc, row, posting_date)
			pe.insert()
			row.db_set({"payment_entry": pe.name, "entry_status": DRAFT_CREATED})
			created.append({"idx": row.idx, "supplier": row.supplier, "payment_entry": pe.name})
		except Exception as e:
			frappe.db.rollback(save_point="spr_row")
			reason = frappe.utils.strip_html(str(e)) or type(e).__name__
			failed.append({"idx": row.idx, "supplier": row.supplier, "reason": reason})
			# The reason is reported in the summary; do not also show it as a separate popup.
			frappe.clear_messages()

	if created and not doc.payment_entries_created:
		doc.db_set("payment_entries_created", 1)

	return {"created": created, "failed": failed, "skipped": skipped}


def build_payment_entry(doc, row, posting_date):
	"""A standard Payment Entry (Pay, to a supplier) for one request row. Not saved here."""
	pe = frappe.new_doc("Payment Entry")
	pe.payment_type = "Pay"
	pe.company = doc.company
	pe.posting_date = posting_date
	pe.party_type = "Supplier"
	pe.party = row.supplier
	pe.paid_from = doc.paid_from_account
	pe.paid_to = row.payable_account
	pe.paid_amount = flt(row.amount)
	pe.received_amount = flt(row.amount)
	pe.source_exchange_rate = 1
	pe.target_exchange_rate = 1
	pe.mode_of_payment = doc.mode_of_payment

	# ERPNext will not save a payment from a bank account without a reference, even as a
	# draft. Where the request gives none, the request number stands in until the user
	# enters the real cheque or transfer reference on the draft.
	pe.reference_no = doc.reference_no or doc.name
	pe.reference_date = doc.reference_date or posting_date

	remarks = row.remarks or doc.remarks
	if remarks:
		pe.custom_remarks = 1
		pe.remarks = remarks

	if pe.meta.has_field("supplier_payment_request"):
		pe.supplier_payment_request = doc.name

	if row.allocation_type == AGAINST_INVOICES:
		allocated = 0.0
		for inv in doc.get("invoices") or []:
			if inv.supplier != row.supplier:
				continue
			# The invoice may have been paid or cancelled since approval: check it again now.
			check_invoice(
				inv.purchase_invoice,
				row.supplier,
				doc.company,
				inv.allocated_amount,
				_("Invoice {0}").format(inv.purchase_invoice),
			)
			pe.append(
				"references",
				{
					"reference_doctype": "Purchase Invoice",
					"reference_name": inv.purchase_invoice,
					"allocated_amount": flt(inv.allocated_amount),
				},
			)
			allocated += flt(inv.allocated_amount)
		if flt(allocated, 2) > flt(row.amount, 2):
			frappe.throw(_("Invoices add up to more than the row amount."))

	pe.setup_party_account_field()
	pe.set_missing_values()
	return pe


# ---------------------------------------------------------------- Payment Entry events
# Called from hooks.py. They keep the request row right even when the user works in the
# Payment Entry form directly.


def on_payment_entry_submit(doc, method=None):
	for row in _rows_for(doc):
		frappe.db.set_value(ITEM, row, "entry_status", SUBMITTED)


def on_payment_entry_cancel(doc, method=None):
	_release_rows(doc)


def on_payment_entry_trash(doc, method=None):
	_release_rows(doc)


def _release_rows(doc):
	"""The entry is gone: free the row so a new entry can be created for it."""
	for row in _rows_for(doc):
		frappe.db.set_value(ITEM, row, {"payment_entry": None, "entry_status": NOT_CREATED})


def _rows_for(doc):
	# Payments that did not come from a request stop here, without touching the database.
	if not doc.get("supplier_payment_request"):
		return []
	return frappe.get_all(
		ITEM, filters={"payment_entry": doc.name, "parenttype": "Supplier Payment Request"}, pluck="name"
	)
