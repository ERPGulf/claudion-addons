import os

import frappe
from frappe.modules.import_file import import_file_by_path

from claudion_addons.supplier_payment_request.setup import create_default_workflow

APP = "claudion_addons"
MODULE = "Supplier Payment Request"
MODULE_KEY = "supplier_payment_request"
MODULE_MAP_CACHE_KEYS = ("app_modules", "installed_app_modules", "module_app", "module_installed_app")

# Child tables first, then the request itself.
DOCTYPES = (
	"supplier_payment_request_item",
	"supplier_payment_request_invoice",
	"supplier_payment_request",
)


def execute():
	"""Sites that already had the app: give them the new documents and the starting workflow once.

	This patch does not rely on the migrate having picked up the new module. On some Frappe
	versions the list of modules used during a migrate is the one from before the update, so
	the module's documents are skipped and "Module not found" is raised for it. The patch
	therefore registers the module itself and loads the documents straight from their files.
	"""
	register_module()

	folder = os.path.join(frappe.get_app_path(APP), MODULE_KEY, "doctype")
	for doctype in DOCTYPES:
		import_file_by_path(os.path.join(folder, doctype, f"{doctype}.json"), force=True)
	frappe.clear_cache(doctype="Supplier Payment Request")

	create_default_workflow()


def register_module():
	"""Make the new module known: its Module Def row, the cached module list, and this process."""
	if not frappe.db.exists("Module Def", MODULE):
		frappe.get_doc({"doctype": "Module Def", "module_name": MODULE, "app_name": APP}).insert(
			ignore_permissions=True
		)

	# Drop any cached module list from before the update, so that it is rebuilt from modules.txt.
	frappe.cache.delete_value(MODULE_MAP_CACHE_KEYS)
	client_cache = getattr(frappe, "client_cache", None)
	if client_cache:
		for key in MODULE_MAP_CACHE_KEYS:
			client_cache.delete_value(key)

	# And put it into the lists this process is already holding.
	if frappe.local.module_app is None:
		frappe.local.module_app = {}
	if frappe.local.app_modules is None:
		frappe.local.app_modules = {}
	frappe.local.module_app[MODULE_KEY] = APP
	modules = frappe.local.app_modules.setdefault(APP, [])
	if MODULE_KEY not in modules:
		modules.append(MODULE_KEY)
