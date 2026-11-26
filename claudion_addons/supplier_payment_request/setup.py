"""Set-up for Supplier Payment Request.

Two things are created on a site:

* a read-only link on Payment Entry back to its request (checked on every migrate);
* a default approval workflow, created ONCE and never touched again. Approval levels,
  approver roles and amount limits differ from client to client, so from then on the
  workflow belongs to the site: edit it there. It is deliberately not a fixture, because
  a fixture would overwrite the client's changes on every migrate.
"""

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

DOCTYPE = "Supplier Payment Request"
WORKFLOW_NAME = "Supplier Payment Request Approval"

CUSTOM_FIELDS = {
	"Payment Entry": [
		{
			"fieldname": "supplier_payment_request",
			"fieldtype": "Link",
			"label": "Supplier Payment Request",
			"options": DOCTYPE,
			"read_only": 1,
			"no_copy": 1,
			"print_hide": 1,
			"insert_after": "payment_order",
		},
	],
}


def after_install():
	setup_custom_fields()
	create_default_workflow()


def setup_custom_fields():
	"""Create the field, or bring an existing one in line. Safe to run any number of times."""
	create_custom_fields(CUSTOM_FIELDS, update=True)


def create_default_workflow():
	"""Create the starting workflow, unless the site already has any workflow for the document."""
	if frappe.db.exists("Workflow", {"document_type": DOCTYPE}):
		return

	states = [
		# state, docstatus, role that may edit in this state, style
		("Draft", 0, "Accounts User", ""),
		("Pending Approval", 0, "Accounts Manager", "Warning"),
		("Approved", 1, "Accounts Manager", "Success"),
		("Rejected", 0, "Accounts User", "Danger"),
		("Cancelled", 2, "Accounts Manager", "Inverse"),
	]
	transitions = [
		# from, action, to, role, condition
		("Draft", "Submit for Approval", "Pending Approval", "Accounts User", None),
		("Draft", "Submit for Approval", "Pending Approval", "Accounts Manager", None),
		("Pending Approval", "Approve", "Approved", "Accounts Manager", None),
		("Pending Approval", "Reject", "Rejected", "Accounts Manager", None),
		("Rejected", "Revise", "Draft", "Accounts User", None),
		("Rejected", "Revise", "Draft", "Accounts Manager", None),
		("Approved", "Cancel", "Cancelled", "Accounts Manager", "not doc.payment_entries_created"),
	]

	for state, _docstatus, _role, style in states:
		if not frappe.db.exists("Workflow State", state):
			frappe.get_doc(
				{"doctype": "Workflow State", "workflow_state_name": state, "style": style}
			).insert(ignore_permissions=True)
	for action in {t[1] for t in transitions}:
		if not frappe.db.exists("Workflow Action Master", action):
			frappe.get_doc({"doctype": "Workflow Action Master", "workflow_action_name": action}).insert(
				ignore_permissions=True
			)

	frappe.get_doc(
		{
			"doctype": "Workflow",
			"workflow_name": WORKFLOW_NAME,
			"document_type": DOCTYPE,
			"is_active": 1,
			"send_email_alert": 0,
			"workflow_state_field": "workflow_state",
			"states": [
				{"state": state, "doc_status": str(docstatus), "allow_edit": role}
				for state, docstatus, role, _style in states
			],
			"transitions": [
				{
					"state": source,
					"action": action,
					"next_state": target,
					"allowed": role,
					"allow_self_approval": 1,
					"condition": condition,
				}
				for source, action, target, role, condition in transitions
			],
		}
	).insert(ignore_permissions=True)
