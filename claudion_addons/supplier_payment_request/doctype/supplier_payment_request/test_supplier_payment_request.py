# Copyright (c) 2026, ERPGulf and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import flt, today

from claudion_addons.supplier_payment_request.payment_entries import create_payment_entries
from claudion_addons.supplier_payment_request.setup import WORKFLOW_NAME, create_default_workflow

# The tests build their own company and masters, so they need none of ERPNext's test records.
IGNORE_TEST_RECORD_DEPENDENCIES = [
	"Company",
	"Account",
	"Supplier",
	"Purchase Invoice",
	"Payment Entry",
	"Mode of Payment",
	"Currency",
]

COMPANY = "SPR Test Co"
ABBR = "SPRT"


class IntegrationTestSupplierPaymentRequest(IntegrationTestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		frappe.set_user("Administrator")
		if not frappe.db.exists("Company", COMPANY):
			frappe.get_doc(
				{
					"doctype": "Company",
					"company_name": COMPANY,
					"abbr": ABBR,
					"default_currency": "SAR",
					"country": "Saudi Arabia",
				}
			).insert()
		cls.bank = frappe.db.get_value(
			"Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}
		) or cls.make_account("SPR Bank", "Bank", "Bank Accounts")
		cls.cash = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Cash", "is_group": 0})
		cls.suppliers = [cls.make_supplier(f"SPR Supplier {n}") for n in ("A", "B", "C")]
		if not frappe.db.exists("Item", "SPR-ITEM"):
			frappe.get_doc(
				{
					"doctype": "Item",
					"item_code": "SPR-ITEM",
					"item_group": frappe.db.get_value("Item Group", {"is_group": 0}),
					"stock_uom": "Nos",
					"is_stock_item": 0,
				}
			).insert()

	@classmethod
	def make_account(cls, name, account_type, parent):
		return (
			frappe.get_doc(
				{
					"doctype": "Account",
					"account_name": name,
					"company": COMPANY,
					"account_type": account_type,
					"parent_account": f"{parent} - {ABBR}",
				}
			)
			.insert()
			.name
		)

	@classmethod
	def make_supplier(cls, name):
		existing = frappe.db.get_value("Supplier", {"supplier_name": name})
		if existing:
			return existing
		return (
			frappe.get_doc(
				{
					"doctype": "Supplier",
					"supplier_name": name,
					"supplier_group": frappe.db.get_value("Supplier Group", {"is_group": 0}),
				}
			)
			.insert()
			.name
		)

	def setUp(self):
		frappe.set_user("Administrator")
		# Most tests exercise the document without a workflow: approval is then a plain submit.
		frappe.db.set_value("Workflow", {"document_type": "Supplier Payment Request"}, "is_active", 0)
		frappe.clear_cache(doctype="Supplier Payment Request")

	def make_invoice(self, supplier, amount):
		pi = frappe.get_doc(
			{
				"doctype": "Purchase Invoice",
				"supplier": supplier,
				"company": COMPANY,
				"posting_date": today(),
				"bill_no": frappe.generate_hash(length=6),
				"items": [{"item_code": "SPR-ITEM", "qty": 1, "rate": amount}],
			}
		).insert()
		pi.submit()
		return pi

	def make_request(self, rows, invoices=None, submit=True, **kw):
		doc = frappe.get_doc(
			{
				"doctype": "Supplier Payment Request",
				"company": COMPANY,
				"paid_from_account": self.bank,
				"items": rows,
				"invoices": invoices or [],
				**kw,
			}
		).insert()
		if submit:
			doc.submit()
		return doc

	def run_action(self, doc, rows=None):
		rows = rows if rows is not None else [r.name for r in doc.items]
		result = create_payment_entries(doc.name, frappe.as_json(rows), posting_date=today())
		doc.reload()
		return result

	# -------------------------------------------------------------- the request

	def test_mixed_request_and_totals(self):
		from claudion_addons.supplier_payment_request.doctype.supplier_payment_request.supplier_payment_request import (
			get_supplier_details,
		)

		a, b, _c = self.suppliers
		owed_before = get_supplier_details(b, COMPANY).outstanding_payable
		pi = self.make_invoice(b, 500)
		doc = self.make_request(
			[
				{"supplier": a, "amount": 100},
				{"supplier": b, "amount": 400, "allocation_type": "Against Invoices"},
			],
			[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 300}],
			submit=False,
		)
		self.assertEqual(doc.total_amount, 500)
		self.assertEqual(doc.currency, "SAR")
		self.assertTrue(doc.items[0].payable_account)
		self.assertEqual(flt(doc.items[1].outstanding_payable), owed_before + 500)
		self.assertEqual(flt(doc.invoices[0].invoice_outstanding), 500)

	def test_validations(self):
		a, b, _c = self.suppliers
		pi = self.make_invoice(b, 200)
		bad = [
			# amount must be positive
			([{"supplier": a, "amount": 0}], []),
			# an On Account supplier cannot have invoice rows
			(
				[{"supplier": b, "amount": 100}],
				[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 50}],
			),
			# Against Invoices needs an invoice
			([{"supplier": b, "amount": 100, "allocation_type": "Against Invoices"}], []),
			# cannot allocate more than the invoice's outstanding
			(
				[{"supplier": b, "amount": 900, "allocation_type": "Against Invoices"}],
				[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 201}],
			),
			# invoices cannot add up to more than the row
			(
				[{"supplier": b, "amount": 100, "allocation_type": "Against Invoices"}],
				[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 150}],
			),
			# the invoice must be the supplier's own
			(
				[{"supplier": a, "amount": 100, "allocation_type": "Against Invoices"}],
				[{"supplier": a, "purchase_invoice": pi.name, "allocated_amount": 50}],
			),
		]
		for rows, invoices in bad:
			with self.assertRaises(frappe.ValidationError, msg=str(rows)):
				self.make_request(rows, invoices, submit=False)

	def test_supplier_on_hold_is_refused(self):
		c = self.suppliers[2]
		frappe.db.set_value("Supplier", c, {"on_hold": 1, "hold_type": "Payments"})
		try:
			with self.assertRaises(frappe.ValidationError):
				self.make_request([{"supplier": c, "amount": 10}], submit=False)
		finally:
			frappe.db.set_value("Supplier", c, {"on_hold": 0, "hold_type": ""})

	# ---------------------------------------------------- creating the entries

	def test_approval_posts_nothing(self):
		a = self.suppliers[0]
		before = frappe.db.count("Payment Entry")
		gl_before = frappe.db.count("GL Entry")
		doc = self.make_request([{"supplier": a, "amount": 100}])
		self.assertEqual(frappe.db.count("Payment Entry"), before)
		self.assertEqual(frappe.db.count("GL Entry"), gl_before)
		self.assertEqual(doc.items[0].entry_status, "Not Created")

	def test_not_before_approval(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}], submit=False)
		with self.assertRaises(frappe.ValidationError):
			create_payment_entries(doc.name, frappe.as_json([doc.items[0].name]))

	def test_drafts_subset_and_no_duplicates(self):
		a, b, _c = self.suppliers
		pi = self.make_invoice(b, 500)
		doc = self.make_request(
			[
				{"supplier": a, "amount": 100, "remarks": "advance"},
				{"supplier": b, "amount": 400, "allocation_type": "Against Invoices"},
			],
			[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 300}],
		)

		# only the chosen row
		result = self.run_action(doc, [doc.items[0].name])
		self.assertEqual(len(result["created"]), 1)
		self.assertEqual(doc.items[0].entry_status, "Draft Created")
		self.assertEqual(doc.items[1].entry_status, "Not Created")
		self.assertEqual(doc.payment_entries_created, 1)

		pe = frappe.get_doc("Payment Entry", doc.items[0].payment_entry)
		self.assertEqual(pe.docstatus, 0)
		self.assertEqual((pe.payment_type, pe.party_type, pe.party), ("Pay", "Supplier", a))
		self.assertEqual((pe.paid_from, pe.paid_to), (self.bank, doc.items[0].payable_account))
		self.assertEqual(flt(pe.paid_amount), 100)
		self.assertEqual(len(pe.references), 0)
		self.assertEqual(flt(pe.unallocated_amount), 100)
		self.assertEqual(pe.remarks, "advance")
		self.assertEqual(pe.supplier_payment_request, doc.name)

		# running everything again creates only the missing row
		result = self.run_action(doc)
		self.assertEqual(len(result["created"]), 1)
		self.assertEqual(len(result["skipped"]), 1)
		self.assertEqual(doc.items[0].payment_entry, pe.name)

		pe2 = frappe.get_doc("Payment Entry", doc.items[1].payment_entry)
		self.assertEqual(pe2.docstatus, 0)
		self.assertEqual(
			[(r.reference_name, flt(r.allocated_amount)) for r in pe2.references], [(pi.name, 300)]
		)
		self.assertEqual(flt(pe2.unallocated_amount), 100)

		# and a third run creates nothing
		result = self.run_action(doc)
		self.assertEqual(len(result["created"]), 0)
		self.assertEqual(frappe.db.count("Payment Entry", {"supplier_payment_request": doc.name}), 2)

	def test_invoice_rechecked_and_one_failure_does_not_stop_the_rest(self):
		a, b, _c = self.suppliers
		pi = self.make_invoice(b, 300)
		doc = self.make_request(
			[
				{"supplier": b, "amount": 300, "allocation_type": "Against Invoices"},
				{"supplier": a, "amount": 50},
			],
			[{"supplier": b, "purchase_invoice": pi.name, "allocated_amount": 300}],
		)
		# the invoice is paid some other way after approval
		other = frappe.get_doc(
			{
				"doctype": "Payment Entry",
				"payment_type": "Pay",
				"company": COMPANY,
				"posting_date": today(),
				"party_type": "Supplier",
				"party": b,
				"paid_from": self.cash,
				"paid_to": doc.items[0].payable_account,
				"paid_amount": 200,
				"received_amount": 200,
				"source_exchange_rate": 1,
				"target_exchange_rate": 1,
				"references": [
					{
						"reference_doctype": "Purchase Invoice",
						"reference_name": pi.name,
						"allocated_amount": 200,
					}
				],
			}
		).insert()
		other.submit()

		result = self.run_action(doc)
		self.assertEqual([r["supplier"] for r in result["failed"]], [b])
		self.assertEqual([r["supplier"] for r in result["created"]], [a])
		self.assertEqual(doc.items[0].entry_status, "Not Created")
		self.assertFalse(doc.items[0].payment_entry)
		self.assertEqual(doc.items[1].entry_status, "Draft Created")

	# ------------------------------------------------------- status and locks

	def test_row_follows_its_payment_entry(self):
		a = self.suppliers[0]
		doc = self.make_request([{"supplier": a, "amount": 100}])
		self.run_action(doc)
		pe = frappe.get_doc("Payment Entry", doc.items[0].payment_entry)

		pe.submit()
		doc.reload()
		self.assertEqual(doc.items[0].entry_status, "Submitted")

		pe.cancel()
		doc.reload()
		self.assertEqual(doc.items[0].entry_status, "Not Created")
		self.assertFalse(doc.items[0].payment_entry)

		# the row can be done again, and a deleted draft frees it again
		self.run_action(doc)
		draft = doc.items[0].payment_entry
		self.assertNotEqual(draft, pe.name)
		frappe.delete_doc("Payment Entry", draft)
		doc.reload()
		self.assertEqual(doc.items[0].entry_status, "Not Created")
		self.assertFalse(doc.items[0].payment_entry)

		# the request stays locked although no entry is left
		self.assertEqual(doc.payment_entries_created, 1)
		with self.assertRaises(frappe.ValidationError):
			doc.cancel()

	def test_cancel_allowed_until_entries_exist(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}])
		doc.cancel()
		self.assertEqual(doc.docstatus, 2)

	def test_approved_request_is_read_only(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}])
		doc.items[0].amount = 999
		with self.assertRaises(frappe.ValidationError):
			doc.save()

	def test_needs_payment_entry_permission(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}])
		user = "spr-accounts-user@example.com"
		if not frappe.db.exists("User", user):
			u = frappe.get_doc(
				{"doctype": "User", "email": user, "first_name": "SPR", "send_welcome_email": 0}
			)
			u.insert()
			u.add_roles("Purchase User")
		frappe.set_user(user)
		try:
			with self.assertRaises(frappe.PermissionError):
				create_payment_entries(doc.name, frappe.as_json([doc.items[0].name]))
		finally:
			frappe.set_user("Administrator")

	# ---------------------------------------------------------------- workflow

	def test_default_workflow(self):
		from frappe.model.workflow import apply_workflow, get_transitions

		create_default_workflow()
		frappe.db.set_value("Workflow", WORKFLOW_NAME, "is_active", 1)
		frappe.clear_cache(doctype="Supplier Payment Request")
		# running it again must not create a second workflow
		create_default_workflow()
		self.assertEqual(frappe.db.count("Workflow", {"document_type": "Supplier Payment Request"}), 1)

		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}], submit=False)
		self.assertEqual(doc.workflow_state, "Draft")
		doc = apply_workflow(doc, "Submit for Approval")
		self.assertEqual((doc.workflow_state, doc.docstatus), ("Pending Approval", 0))
		doc = apply_workflow(doc, "Reject")
		doc = apply_workflow(doc, "Revise")
		doc = apply_workflow(doc, "Submit for Approval")
		doc = apply_workflow(doc, "Approve")
		self.assertEqual((doc.workflow_state, doc.docstatus), ("Approved", 1))
		self.assertIn("Cancel", [t.action for t in get_transitions(doc)])

		self.run_action(doc)
		# once entries exist the Cancel action is no longer offered
		self.assertNotIn("Cancel", [t.action for t in get_transitions(doc)])
