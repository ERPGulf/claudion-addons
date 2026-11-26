# Copyright (c) 2026, ERPGulf and contributors
# For license information, please see license.txt

"""Supplier Payment Request: one request, many supplier payments, approved together.

The request itself posts nothing. Once it is approved (submitted), a user who may create
Payment Entries turns its rows into draft Payment Entries (see ../../payment_entries.py).

Nothing here depends on the names of workflow states or on particular roles. "Approved"
means submitted (docstatus 1), so a site can run any workflow it likes on this document,
or none at all.
"""

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, getdate, today

from erpnext.accounts.party import get_party_account

ON_ACCOUNT = "On Account"
AGAINST_INVOICES = "Against Invoices"


class SupplierPaymentRequest(Document):
	def validate(self):
		self.validate_paid_from_account()
		self.validate_items()
		self.validate_invoices()
		self.total_amount = sum(flt(row.amount) for row in self.items)

	def before_cancel(self):
		# Hard rule: once payment entries have been created from this request it can never be
		# cancelled, even if those entries were cancelled or deleted afterwards.
		if self.payment_entries_created:
			frappe.throw(
				_(
					"Payment entries have been created from this request, so it cannot be cancelled. "
					"Cancel or delete the payment entries themselves if a payment is not to be made."
				),
				title=_("Cannot Cancel"),
			)

	# ------------------------------------------------------------------ header

	def validate_paid_from_account(self):
		if not self.paid_from_account:
			return
		account = validate_paid_from_account(self.paid_from_account, self.company)
		self.currency = account.account_currency

	# ------------------------------------------------------------------- items

	def validate_items(self):
		seen = set()
		against_invoices = set()

		for row in self.items:
			if flt(row.amount) <= 0:
				frappe.throw(_("Row {0}: Amount must be greater than zero.").format(row.idx))

			details = get_supplier_details(row.supplier, self.company)
			if details.disabled:
				frappe.throw(
					_("Row {0}: Supplier {1} is disabled.").format(row.idx, frappe.bold(row.supplier))
				)
			if details.on_hold:
				frappe.throw(
					_("Row {0}: Supplier {1} is on hold for payments.").format(
						row.idx, frappe.bold(row.supplier)
					)
				)

			row.supplier_name = details.supplier_name
			row.payable_account = details.payable_account
			row.outstanding_payable = details.outstanding_payable
			row.allocation_type = row.allocation_type or ON_ACCOUNT

			if details.payable_account_currency != self.currency:
				frappe.throw(
					_(
						"Row {0}: Supplier {1} is payable in {2}, but the Paid From Account is in {3}. "
						"Payments across currencies are not supported in a Supplier Payment Request."
					).format(
						row.idx, frappe.bold(row.supplier), details.payable_account_currency, self.currency
					)
				)

			if row.allocation_type == AGAINST_INVOICES:
				if row.supplier in against_invoices:
					frappe.throw(
						_(
							"Row {0}: Supplier {1} already has an Against Invoices row. "
							"Put all of that supplier's invoices under one row."
						).format(row.idx, frappe.bold(row.supplier))
					)
				against_invoices.add(row.supplier)

			key = (row.supplier, flt(row.amount))
			if key in seen:
				frappe.msgprint(
					_("Row {0}: Supplier {1} appears more than once with the same amount.").format(
						row.idx, frappe.bold(row.supplier)
					),
					title=_("Possible Duplicate"),
					indicator="orange",
				)
			seen.add(key)

	# ---------------------------------------------------------------- invoices

	def validate_invoices(self):
		"""Invoice rows belong to the supplier's Against Invoices row."""
		item_rows = {row.supplier: row for row in self.items if row.allocation_type == AGAINST_INVOICES}
		allocated = dict.fromkeys(item_rows, 0.0)
		seen = set()

		for inv in self.get("invoices") or []:
			if inv.supplier not in item_rows:
				frappe.throw(
					_(
						"Invoices row {0}: Supplier {1} has no payment row set to Against Invoices. "
						"Remove the invoice, or change the supplier's Allocation Type."
					).format(inv.idx, frappe.bold(inv.supplier))
				)
			if inv.purchase_invoice in seen:
				frappe.throw(
					_("Invoices row {0}: {1} is entered more than once.").format(
						inv.idx, inv.purchase_invoice
					)
				)
			seen.add(inv.purchase_invoice)

			inv.invoice_outstanding = check_invoice(
				inv.purchase_invoice,
				inv.supplier,
				self.company,
				inv.allocated_amount,
				_("Invoices row {0}").format(inv.idx),
			)
			allocated[inv.supplier] += flt(inv.allocated_amount)

		for supplier, row in item_rows.items():
			if not allocated[supplier]:
				frappe.throw(
					_("Row {0}: Add at least one invoice for {1}, or set the row to On Account.").format(
						row.idx, frappe.bold(supplier)
					)
				)
			if flt(allocated[supplier], 2) > flt(row.amount, 2):
				frappe.throw(
					_("Row {0}: Invoices for {1} add up to {2}, more than the row amount {3}.").format(
						row.idx, frappe.bold(supplier), allocated[supplier], row.amount
					)
				)


def validate_paid_from_account(account, company):
	"""The account money is paid from: a bank or cash ledger of the company, in company currency."""
	acc = frappe.db.get_value(
		"Account",
		account,
		["company", "account_type", "is_group", "disabled", "account_currency"],
		as_dict=True,
	)
	if not acc:
		frappe.throw(_("Account {0} does not exist.").format(account))
	if acc.company != company:
		frappe.throw(_("Paid From Account {0} does not belong to {1}.").format(account, company))
	if acc.is_group or acc.disabled or acc.account_type not in ("Bank", "Cash"):
		frappe.throw(_("Paid From Account {0} must be an active Bank or Cash account.").format(account))

	company_currency = frappe.get_cached_value("Company", company, "default_currency")
	acc.account_currency = acc.account_currency or company_currency
	if acc.account_currency != company_currency:
		frappe.throw(
			_(
				"Paid From Account {0} is in {1}. A Supplier Payment Request supports accounts in the "
				"company currency ({2}) only."
			).format(account, acc.account_currency, company_currency)
		)
	return acc


def check_invoice(purchase_invoice, supplier, company, allocated_amount, where):
	"""Check one invoice allocation against the invoice as it stands now. Returns its outstanding."""
	pi = frappe.db.get_value(
		"Purchase Invoice",
		purchase_invoice,
		["supplier", "company", "docstatus", "outstanding_amount"],
		as_dict=True,
	)
	if not pi or pi.docstatus != 1:
		frappe.throw(_("{0}: {1} is not a submitted purchase invoice.").format(where, purchase_invoice))
	if pi.supplier != supplier or pi.company != company:
		frappe.throw(
			_("{0}: {1} does not belong to supplier {2} in {3}.").format(
				where, purchase_invoice, supplier, company
			)
		)
	if flt(allocated_amount) <= 0:
		frappe.throw(_("{0}: Allocated Amount must be greater than zero.").format(where))
	if flt(allocated_amount, 2) > flt(pi.outstanding_amount, 2):
		frappe.throw(
			_("{0}: Allocated Amount {1} is more than the outstanding {2} of {3}.").format(
				where, flt(allocated_amount), flt(pi.outstanding_amount), purchase_invoice
			)
		)
	return flt(pi.outstanding_amount)


@frappe.whitelist()
def get_supplier_details(supplier, company):
	"""Payable account and current payable balance of a supplier, for a payment row."""
	if not supplier or not company:
		return frappe._dict()
	frappe.has_permission("Supplier", "read", supplier, throw=True)

	sup = frappe.db.get_value(
		"Supplier",
		supplier,
		["supplier_name", "disabled", "on_hold", "hold_type", "release_date"],
		as_dict=True,
	)
	if not sup:
		frappe.throw(_("Supplier {0} does not exist.").format(supplier))

	on_hold = bool(
		sup.on_hold
		and (sup.hold_type or "All") in ("All", "Payments")
		and (not sup.release_date or getdate(sup.release_date) > getdate(today()))
	)

	payable_account = get_party_account("Supplier", supplier, company)
	payable_account_currency = frappe.db.get_value(
		"Account", payable_account, "account_currency"
	) or frappe.get_cached_value("Company", company, "default_currency")

	gle = frappe.qb.DocType("GL Entry")
	from frappe.query_builder.functions import Sum

	balance = (
		frappe.qb.from_(gle)
		.select(Sum(gle.credit) - Sum(gle.debit))
		.where(
			(gle.party_type == "Supplier")
			& (gle.party == supplier)
			& (gle.company == company)
			& (gle.is_cancelled == 0)
		)
	).run()

	return frappe._dict(
		supplier_name=sup.supplier_name,
		disabled=bool(sup.disabled),
		on_hold=on_hold,
		payable_account=payable_account,
		payable_account_currency=payable_account_currency,
		outstanding_payable=flt(balance[0][0]) if balance else 0.0,
	)
