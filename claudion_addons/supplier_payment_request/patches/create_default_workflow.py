from claudion_addons.supplier_payment_request.setup import create_default_workflow


def execute():
	"""Sites that already had the app: give them the starting workflow once."""
	create_default_workflow()
