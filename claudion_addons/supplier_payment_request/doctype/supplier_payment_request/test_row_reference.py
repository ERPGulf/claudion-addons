# Copyright (c) 2026, ERPGulf and contributors
# For license information, please see license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_days, getdate, today

from claudion_addons.supplier_payment_request.payment_entries import create_payment_entries

IGNORE_TEST_RECORD_DEPENDENCIES = [
	"Company",
	"Account",
	"Supplier",
	"Payment Entry",
	"Mode of Payment",
	"Currency",
]

COMPANY = "SPR Ref Test Co"
ABBR = "SPRR"


class IntegrationTestRowReference(IntegrationTestCase):
	"""Each supplier row can carry its own cheque or transfer reference."""

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
		) or (
			frappe.get_doc(
				{
					"doctype": "Account",
					"account_name": "SPR Ref Bank",
					"company": COMPANY,
					"account_type": "Bank",
					"parent_account": f"Bank Accounts - {ABBR}",
				}
			)
			.insert()
			.name
		)
		cls.suppliers = []
		for n in ("A", "B", "C"):
			name = f"SPR Ref Supplier {n}"
			cls.suppliers.append(
				frappe.db.get_value("Supplier", {"supplier_name": name})
				or frappe.get_doc(
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
		frappe.db.set_value("Workflow", {"document_type": "Supplier Payment Request"}, "is_active", 0)
		frappe.clear_cache(doctype="Supplier Payment Request")

	def make_request(self, rows, **kw):
		doc = frappe.get_doc(
			{
				"doctype": "Supplier Payment Request",
				"company": COMPANY,
				"paid_from_account": self.bank,
				"items": rows,
				**kw,
			}
		).insert()
		doc.submit()
		return doc

	def entry(self, row):
		return frappe.get_doc("Payment Entry", row.payment_entry)

	def test_reference_per_row(self):
		a, b, c = self.suppliers
		yesterday = add_days(today(), -1)
		doc = self.make_request(
			[
				# given on the row when the request was raised
				{"supplier": a, "amount": 100, "reference_no": "CHQ-001", "reference_date": yesterday},
				# given later, when the entries are created
				{"supplier": b, "amount": 200},
				# never given: falls back to the request's own reference
				{"supplier": c, "amount": 300},
			],
			reference_no="BATCH-9",
		)
		rows = [
			doc.items[0].name,
			{"name": doc.items[1].name, "reference_no": " TRF-777 ", "reference_date": yesterday},
			{"name": doc.items[2].name, "reference_no": "", "reference_date": None},
		]
		create_payment_entries(doc.name, frappe.as_json(rows), posting_date=today())
		doc.reload()

		first, second, third = (self.entry(row) for row in doc.items)
		self.assertEqual((first.reference_no, getdate(first.reference_date)), ("CHQ-001", getdate(yesterday)))
		self.assertEqual(
			(second.reference_no, getdate(second.reference_date)), ("TRF-777", getdate(yesterday))
		)
		self.assertEqual((third.reference_no, getdate(third.reference_date)), ("BATCH-9", getdate(today())))

		# what was typed when creating is kept on the request row
		self.assertEqual(doc.items[1].reference_no, "TRF-777")
		self.assertEqual(getdate(doc.items[1].reference_date), getdate(yesterday))

	def test_no_reference_anywhere_uses_request_number(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}])
		create_payment_entries(doc.name, frappe.as_json([doc.items[0].name]), posting_date=today())
		doc.reload()
		self.assertEqual(self.entry(doc.items[0]).reference_no, doc.name)

	def test_reference_can_be_added_after_approval(self):
		doc = self.make_request([{"supplier": self.suppliers[0], "amount": 100}])
		doc.items[0].reference_no = "CHQ-LATE"
		doc.save()
		create_payment_entries(doc.name, frappe.as_json([doc.items[0].name]), posting_date=today())
		doc.reload()
		self.assertEqual(self.entry(doc.items[0]).reference_no, "CHQ-LATE")
