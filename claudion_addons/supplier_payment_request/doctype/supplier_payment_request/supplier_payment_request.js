// Copyright (c) 2026, ERPGulf and contributors
// For license information, please see license.txt

const SPR_AGAINST_INVOICES = "Against Invoices";

frappe.ui.form.on("Supplier Payment Request", {
	setup(frm) {
		frm.set_query("paid_from_account", () => ({
			filters: {
				company: frm.doc.company,
				account_type: ["in", ["Bank", "Cash"]],
				is_group: 0,
				disabled: 0,
			},
		}));

		// Invoices can be entered only for suppliers whose payment row is Against Invoices.
		frm.set_query("supplier", "invoices", () => ({
			filters: { name: ["in", spr_invoice_suppliers(frm)] },
		}));

		frm.set_query("purchase_invoice", "invoices", (doc, cdt, cdn) => {
			const row = locals[cdt][cdn];
			return {
				filters: {
					supplier: row.supplier,
					company: doc.company,
					docstatus: 1,
					outstanding_amount: [">", 0],
				},
			};
		});
	},

	refresh(frm) {
		const pending = (frm.doc.items || []).filter((row) => !row.payment_entry);

		// Approved means submitted. Who may create the entries follows the site's
		// permissions on Payment Entry, so no role is named here.
		if (frm.doc.docstatus === 1 && pending.length && frappe.model.can_create("Payment Entry")) {
			frm.add_custom_button(__("Create Payment Entries"), () => spr_open_dialog(frm)).addClass(
				"btn-primary"
			);
		}
	},

	company(frm) {
		(frm.doc.items || []).forEach((row) => spr_fetch_supplier(frm, row.doctype, row.name));
	},
});

frappe.ui.form.on("Supplier Payment Request Item", {
	supplier(frm, cdt, cdn) {
		spr_fetch_supplier(frm, cdt, cdn);
	},
	amount(frm) {
		spr_set_total(frm);
	},
	items_remove(frm) {
		spr_set_total(frm);
	},
});

frappe.ui.form.on("Supplier Payment Request Invoice", {
	invoices_add(frm, cdt, cdn) {
		// With one Against Invoices supplier there is nothing to choose.
		const suppliers = spr_invoice_suppliers(frm);
		if (suppliers.length === 1) {
			frappe.model.set_value(cdt, cdn, "supplier", suppliers[0]);
		}
	},
	supplier(frm, cdt, cdn) {
		frappe.model.set_value(cdt, cdn, "purchase_invoice", null);
	},
	purchase_invoice(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		if (!row.purchase_invoice) {
			frappe.model.set_value(cdt, cdn, { invoice_outstanding: 0, allocated_amount: 0 });
			return;
		}
		frappe.db.get_value("Purchase Invoice", row.purchase_invoice, "outstanding_amount").then((r) => {
			const outstanding = (r.message && r.message.outstanding_amount) || 0;
			frappe.model.set_value(cdt, cdn, {
				invoice_outstanding: outstanding,
				allocated_amount: outstanding,
			});
		});
	},
});

function spr_invoice_suppliers(frm) {
	return (frm.doc.items || [])
		.filter((row) => row.allocation_type === SPR_AGAINST_INVOICES && row.supplier)
		.map((row) => row.supplier);
}

function spr_set_total(frm) {
	const total = (frm.doc.items || []).reduce((sum, row) => sum + flt(row.amount), 0);
	frm.set_value("total_amount", total);
}

function spr_fetch_supplier(frm, cdt, cdn) {
	const row = locals[cdt][cdn];
	if (!row.supplier || !frm.doc.company) return;

	frappe.call({
		method: "claudion_addons.supplier_payment_request.doctype.supplier_payment_request.supplier_payment_request.get_supplier_details",
		args: { supplier: row.supplier, company: frm.doc.company },
		callback(r) {
			if (!r.message) return;
			frappe.model.set_value(cdt, cdn, {
				payable_account: r.message.payable_account,
				outstanding_payable: r.message.outstanding_payable,
			});
		},
	});
}

// ------------------------------------------------------------------
// Create Payment Entries: review, choose rows, enter references, confirm
// ------------------------------------------------------------------
function spr_open_dialog(frm) {
	const currency = frm.doc.currency;
	const pending = [];
	const done = [];

	(frm.doc.items || []).forEach((row) => {
		const invoices = (frm.doc.invoices || []).filter((inv) => inv.supplier === row.supplier);
		let allocation = __(row.allocation_type);
		if (row.allocation_type === SPR_AGAINST_INVOICES) {
			allocation += ` (${invoices.map((inv) => inv.purchase_invoice).join(", ")})`;
		}
		if (row.payment_entry) {
			const text = `${row.supplier_name || row.supplier} · ${format_currency(
				row.amount,
				currency
			)} · ${allocation}`;
			done.push(`${frappe.utils.escape_html(text)} · ${row.payment_entry} · ${__(row.entry_status)}`);
		} else {
			pending.push({
				// ticked to start with, using the table's own row boxes
				__checked: 1,
				row_name: row.name,
				supplier_name: row.supplier_name || row.supplier,
				amount: row.amount,
				allocation: allocation,
				reference_no: row.reference_no || frm.doc.reference_no || "",
				reference_date: row.reference_date || frm.doc.reference_date || null,
			});
		}
	});

	const dialog = new frappe.ui.Dialog({
		title: __("Create Payment Entries"),
		size: "extra-large",
		fields: [
			{
				fieldname: "posting_date",
				fieldtype: "Date",
				label: __("Posting Date"),
				reqd: 1,
				default: frm.doc.posting_date || frappe.datetime.get_today(),
			},
			{ fieldtype: "Column Break" },
			{
				fieldname: "paid_from_account",
				fieldtype: "Link",
				label: __("Paid From Account"),
				options: "Account",
				reqd: 1,
				default: frm.doc.paid_from_account,
				get_query: () => ({
					filters: {
						company: frm.doc.company,
						account_type: ["in", ["Bank", "Cash"]],
						is_group: 0,
						disabled: 0,
					},
				}),
			},
			{
				fieldtype: "Section Break",
				label: __("Rows to create"),
				description: __(
					"Untick a row to leave it for later. Enter each supplier's cheque or transfer number and date here, and the draft is created with them."
				),
			},
			{
				fieldname: "rows",
				fieldtype: "Table",
				cannot_add_rows: true,
				cannot_delete_rows: true,
				in_place_edit: true,
				data: pending,
				get_data: () => pending,
				fields: [
					{
						fieldname: "supplier_name",
						fieldtype: "Data",
						label: __("Supplier"),
						read_only: 1,
						in_list_view: 1,
						columns: 4,
					},
					{
						fieldname: "amount",
						fieldtype: "Currency",
						label: __("Amount"),
						options: currency,
						read_only: 1,
						in_list_view: 1,
						columns: 2,
					},
					{
						fieldname: "allocation",
						fieldtype: "Data",
						label: __("Allocation"),
						read_only: 1,
						in_list_view: 1,
						columns: 2,
					},
					{
						fieldname: "reference_no",
						fieldtype: "Data",
						label: __("Reference No"),
						in_list_view: 1,
						columns: 2,
					},
					{
						fieldname: "reference_date",
						fieldtype: "Date",
						label: __("Reference Date"),
						in_list_view: 1,
						columns: 2,
					},
					{ fieldname: "row_name", fieldtype: "Data", hidden: 1 },
				],
			},
			{
				fieldtype: "Section Break",
				label: __("Already created"),
				depends_on: `eval:${done.length > 0}`,
			},
			{
				fieldname: "done_html",
				fieldtype: "HTML",
				options: `<div class="text-muted small">${done.join("<br>")}</div>`,
			},
			{ fieldtype: "Section Break" },
			{
				fieldtype: "HTML",
				options: `<div class="text-muted small">${__(
					"Entries are created as drafts. Nothing is submitted. Invoice outstanding amounts are checked again now."
				)}</div>`,
			},
		],
		primary_action_label: __("Create Drafts"),
		primary_action(values) {
			const rows = pending
				.filter((row) => cint(row.__checked))
				.map((row) => ({
					name: row.row_name,
					reference_no: row.reference_no || "",
					reference_date: row.reference_date || null,
				}));
			if (!rows.length) {
				frappe.msgprint(__("Select at least one row."));
				return;
			}
			dialog.hide();
			frappe.call({
				method: "claudion_addons.supplier_payment_request.payment_entries.create_payment_entries",
				args: {
					request: frm.doc.name,
					rows: rows,
					posting_date: values.posting_date,
					paid_from_account: values.paid_from_account,
				},
				freeze: true,
				freeze_message: __("Creating payment entries..."),
				callback(r) {
					if (r.message) spr_show_result(r.message);
					frm.reload_doc();
				},
			});
		},
	});
	dialog.show();
}

function spr_show_result(result) {
	const esc = frappe.utils.escape_html;
	let html = "";

	if (result.created.length) {
		html += `<p><b>${__("Draft payment entries created")}</b></p><ul>`;
		result.created.forEach((r) => {
			html += `<li>${esc(r.supplier)}: <a href="/app/payment-entry/${encodeURIComponent(
				r.payment_entry
			)}">${esc(r.payment_entry)}</a></li>`;
		});
		html += "</ul>";
	}
	if (result.failed.length) {
		html += `<p><b>${__("Not created")}</b></p><ul>`;
		result.failed.forEach((r) => {
			html += `<li>${__("Row {0}", [r.idx])}, ${esc(r.supplier)}: ${esc(r.reason)}</li>`;
		});
		html += "</ul>";
	}
	if (result.skipped.length) {
		html += `<p><b>${__("Skipped, already created")}</b></p><ul>`;
		result.skipped.forEach((r) => {
			html += `<li>${esc(r.supplier)}: ${esc(r.payment_entry)}</li>`;
		});
		html += "</ul>";
	}

	frappe.msgprint({
		title: __("Create Payment Entries"),
		message: html || __("Nothing to do."),
		indicator: result.failed.length ? "orange" : "green",
		wide: true,
	});
}
