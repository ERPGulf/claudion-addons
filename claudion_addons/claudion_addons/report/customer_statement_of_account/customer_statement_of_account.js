
// const CSA_PRINT_HTML = `
// <!-- Modified on 08-10-2026 : bilingual customer name / address / VAT header -->

// <style>

// body,
// html {
//     margin-top: 10;
//     padding: 0;
//     width: 100%;
//     height: auto;
//     font-family: Arial, sans-serif;
// }

// .title-letter-spacing {
//     letter-spacing: .2rem;
// }

// /* ---------- Customer header (English left / Arabic right) ---------- */
// .customer-details {
//     width: 100%;
//     border-collapse: collapse;
//     font-size: 13px;
//     line-height: 1.35;
//     margin: 6px 0 10px 0;
// }
// .customer-details td {
//     border: none !important;
//     padding: 0 !important;
//     vertical-align: top;
//     width: 50%;
// }
// .customer-details p {
//     margin: 0 0 2px 0;
// }
// .customer-details .field-label {
//     font-weight: bold;
// }
// .customer-details .customer-en {
//     text-align: left;
//     direction: ltr;
// }
// .customer-details .customer-ar {
//     text-align: right;
//     direction: rtl;
// }
// .customer-details .ltr-value,
// .customer-details .num {
//     direction: ltr;
//     unicode-bidi: embed;
// }

// @media print {

//     @page {
//         size: A4;
//         margin-top: 10mm;
//     }

//     .page-break {
//         page-break-before: always;
//         margin-top: 10mm;
//     }

//     thead {
//         display: table-header-group;
//     }

//     tfoot {
//         display: table-footer-group;
//     }

//     th,
//     td {
//         padding: 1px;
//         border: 1px solid black;
//     }

//     .customer-details td {
//         border: none !important;
//         padding: 0 !important;
//     }

//     .no-print {
//         display: none !important;
//     }
// }

// </style>

// <br>

// <div style="font-family:Arial">

// {%
// var show_po_column = false;

// if(!filters.party){
//     show_po_column = true;
// }else{
//     for(var x=0; x<data.length; x++){
//         if(data[x].po_no || data[x].remarks){
//             show_po_column = true;
//             break;
//         }
//     }
// }

// var single_customer = filters.party && (!Array.isArray(filters.party) || filters.party.length == 1);

// /* Customer header details are attached by the .py to the first row */
// var cust = {};
// var all_rows = (typeof original_data !== "undefined" && original_data && original_data.length) ? original_data : data;
// for (var c = 0; c < all_rows.length; c++) {
//     if (all_rows[c] && all_rows[c].cust_name !== undefined) { cust = all_rows[c]; break; }
// }

// var cust_name = cust.cust_name || filters.party_name || (Array.isArray(filters.party) ? filters.party[0] : filters.party) || "";
// var cust_tax_id = cust.cust_tax_id || filters.tax_id || "";
// var cust_name_ar = cust.cust_name_ar || filters.party_name_ar || "";
// var cust_address_en = cust.cust_address_en || filters.address_en || "";
// var cust_address_ar = cust.cust_address_ar || filters.address_ar || "";
// %}

// <div>

// <div style="text-align:center; font-size:15px; line-height:1.4; letter-spacing:0;">
//     <div style="font-weight:bold; font-size:18px; margin-bottom:4px;">
//         {%= __("STATEMENT OF ACCOUNTS") %}
//     </div>

//     {% if (!single_customer) { %}
//         {%= __("All Customers ") %}<br>
//     {% } %}
// </div>

// <div style="text-align:center; font-size:13px;">
//     <b>
//     {%= __("{0} to {1}", [
//         frappe.datetime.str_to_user(filters.from_date),
//         frappe.datetime.str_to_user(filters.to_date)
//     ]) %}
//     </b>
// </div>


// {% if (single_customer) { %}

// <table class="customer-details">
//     <tr>

//         <!-- CUSTOMER — ENGLISH (LEFT) -->
//         <td class="customer-en">

//             <p>
//                 <span class="field-label">Client / Company:</span>
//                 {%= cust_name %}
//             </p>

//             {% if (cust_address_en) { %}
//             <p>
//                 <span class="field-label">Address:</span>
//                 {%= cust_address_en %}
//             </p>
//             {% } %}

//             {% if (cust_tax_id) { %}
//             <p>
//                 <span class="field-label">VAT. No.:</span>
//                 {%= cust_tax_id %}
//             </p>
//             {% } %}

//         </td>

//         <!-- CUSTOMER — ARABIC (RIGHT) -->
//         <td class="customer-ar">

//             <p>
//                 <span class="field-label">العميل / الشركة:</span>
//                 {% if (cust_name_ar) { %}
//                     {%= cust_name_ar %}
//                 {% } else { %}
//                     <span class="ltr-value">{%= cust_name %}</span>
//                 {% } %}
//             </p>

//             {% if (cust_address_ar) { %}
//             <p>
//                 <span class="field-label">العنوان:</span>
//                 {%= cust_address_ar %}
//             </p>
//             {% } %}

//             {% if (cust_tax_id) { %}
//             <p>
//                 <span class="field-label">الرقم الضريبي:</span>
//                 <span class="ltr-value">{%= cust_tax_id %}</span>
//             </p>
//             {% } %}

//         </td>

//     </tr>
// </table>

// {% } else { %}
// <br>
// {% } %}

// </div>


// <table style="width:100%; font-size:11px">

// <thead>

// <tr class="title-letter-spacing" style="text-align:center; font-weight:bold">

// <td style="border:1.5px solid black; width:7em">
// {%= __("Date").toLocaleUpperCase() %}
// </td>

// <td style="border:1.5px solid black">
// {%= __("Particulars").toLocaleUpperCase() %}
// </td>

// {% if(show_po_column) { %}
// <td style="border:1.5px solid black">
// {%= __("Remarks").toLocaleUpperCase() %}
// </td>
// {% } %}

// <td style="border:1.5px solid black; width:9em">
// {%= __("Debit").toLocaleUpperCase() %}
// </td>

// <td style="border:1.5px solid black; width:9em">
// {%= __("Credit").toLocaleUpperCase() %}
// </td>

// <td style="border:1.5px solid black; width:10.2em">
// {%= __("Balance").toLocaleUpperCase() %}
// </td>

// </tr>

// </thead>

// <tbody>

// {% for(var i=0, l=data.length; i<l; i++) { %}

// <tr style="border-bottom:1px solid black">

// {% if(data[i].posting_date) { %}

// <td style="text-align:center; border:1px dotted black">
// {%= frappe.datetime.str_to_user(data[i].posting_date) %}
// </td>

// <td style="border-right:1px dotted black">

// {%= data[i].voucher_type %} {%= data[i].voucher_no %}

// {% if(!(filters.party || filters.account)) { %}
// {%= data[i].party || data[i].account %}
// {% } %}

// <br>

// {% if(data[i].bill_no) { %}
// {%= __("Supplier Invoice No") %}: {%= data[i].bill_no %}
// {% } %}

// </td>


// {% if(show_po_column) { %}

// <td style="border-right:1px dotted black; font-size:10px">

// <!-- Sales Invoice PO -->

// {% if(data[i].po_no) { %}

// {%= __("Remarks") %}:
// {%= __("Customer order against") %}
// {%= data[i].po_no %}
// {%= __("dated") %}
// {%= frappe.datetime.str_to_user(data[i].po_date) %}

// {% } %}


// <!-- Payment Entry reference -->

// {% if(data[i].voucher_type == "Payment Entry") { %}

// {%= __("Remarks") %}:
// {%= __("Customer against") %}
// {%= data[i].reference_no || "" %}
// {%= __("dated") %}
// {%= data[i].reference_date ? frappe.datetime.str_to_user(data[i].reference_date) : "" %}

// {% } %}


// {% if(data[i].remarks) { %}
// <br>
// {%= data[i].remarks %}
// {% } %}

// </td>

// {% } %}


// <!-- DEBIT COLUMN -->

// <td style="text-align:right; border-right:1px dotted black">

// {% if(data[i].debit || data[i].debit == 0) { %}
// {%= format_currency(data[i].debit, filters.presentation_currency) %}
// {% } %}

// </td>


// <!-- CREDIT COLUMN -->

// <td style="text-align:right; border-right:1px dotted black">

// {% if(data[i].credit || data[i].credit == 0) { %}
// {%= format_currency(data[i].credit, filters.presentation_currency) %}
// {% } %}

// </td>


// {% } else { %}


// <td style="text-align:center; border:1px dotted black">

// {% if(i == 0) { %}
// {%= frappe.datetime.str_to_user(filters.from_date) %}
// {% } %}

// </td>


// <td style="text-align:left; border-right:1px dotted black">
// <b>

// {% if(i == l-2) { %}
// {%= __("Total") %}
// {% } else { %}

// {% if(i == l-1) { %}
// {%= __("Closing [Opening + Total] ") %}
// {% } else { %}
// {%= frappe.format(data[i].account, {fieldtype: "Link"}) || "&nbsp;" %}
// {% } %}

// {% } %}

// </b>
// </td>


// {% if(show_po_column) { %}
// <td style="border-right:1px dotted black"></td>
// {% } %}


// <!-- OPENING / TOTAL DEBIT -->

// <td style="text-align:right; border-right:1px dotted black">

// {% if(data[i].debit || data[i].debit == 0) { %}
// {%= format_currency(data[i].debit, filters.presentation_currency) %}
// {% } else { %}
// 0
// {% } %}

// </td>


// <!-- OPENING / TOTAL CREDIT -->

// <td style="text-align:right; border-right:1px dotted black">

// {% if(data[i].credit || data[i].credit == 0) { %}
// {%= format_currency(data[i].credit, filters.presentation_currency) %}
// {% } else { %}
// 0
// {% } %}

// </td>

// {% } %}


// <!-- BALANCE -->

// {% if(i == l-1) { %}

// <td style="text-align:right; font-weight:bold; border-right:1px dotted black">

// {%= format_currency(data[i].balance, filters.presentation_currency) %}

// {% if(data[i].balance < 0){ %}Cr{% } %}
// {% if(data[i].balance > 0){ %}Dr{% } %}

// </td>

// {% } else { %}

// <td style="text-align:right; border-right:1px dotted black">

// {% if(data[i].balance || data[i].balance == 0) { %}
// {%= format_currency(data[i].balance, filters.presentation_currency) %}
// {% } else { %}
// 0
// {% } %}

// </td>

// {% } %}

// </tr>

// {% } %}

// </tbody>

// </table>


// <p class="text-right text-muted">

// {%= __("Printed on {0}",
// [frappe.datetime.str_to_user(frappe.datetime.get_datetime_as_string())]) %}

// </p>

// </div>

// `;

// // ------------------------------------------------------------
// // Helpers: build English / Arabic address HTML from an Address doc
// // ------------------------------------------------------------
// function csa_esc(v) {
// 	return frappe.utils.escape_html(v || "");
// }

// function csa_address_en(a) {
// 	if (!a) return "";
// 	const building_no = a.custom_building_number || a.building_number || "";
// 	const lines = [];

// 	if (a.address_line1) lines.push(csa_esc(a.address_line1));
// 	if (a.address_line2) lines.push(csa_esc(a.address_line2));

// 	if (building_no || a.city || a.pincode) {
// 		let city_line = "";
// 		if (building_no) city_line += "Building No. " + csa_esc(building_no) + ", ";
// 		city_line += csa_esc(a.city);
// 		if (a.pincode) city_line += " " + csa_esc(a.pincode);
// 		lines.push(city_line.trim());
// 	}

// 	if (a.country) lines.push(csa_esc(a.country));
// 	return lines.join("<br>");
// }

// function csa_address_ar(a) {
// 	if (!a) return "";
// 	const building_no = a.custom_building_number || a.building_number || "";
// 	const line1 = a.custom_address_line_1_in_arabic || a.address_line1 || "";
// 	const line2 = a.custom_address_line_2_in_arabic || a.address_line2 || "";
// 	const city = a.custom_city_in_arabic || a.city || "";
// 	const country = a.country === "Saudi Arabia" ? "المملكة العربية السعودية" : a.country || "";
// 	const lines = [];

// 	if (line1) lines.push(csa_esc(line1));
// 	if (line2) lines.push(csa_esc(line2));

// 	if (building_no || city || a.pincode) {
// 		let city_line = "";
// 		if (building_no) city_line += 'رقم المبنى <span class="num">' + csa_esc(building_no) + "</span>، ";
// 		city_line += csa_esc(city);
// 		if (a.pincode) city_line += ' <span class="num">' + csa_esc(a.pincode) + "</span>";
// 		lines.push(city_line.trim());
// 	}

// 	if (country) lines.push(csa_esc(country));
// 	return lines.join("<br>");
// }

// // ------------------------------------------------------------
// // Load customer + address and store in hidden filters (for print)
// // ------------------------------------------------------------
// async function csa_set_customer_details() {
// 	let customers = frappe.query_report.get_filter_value("party");

// 	// Always normalize to array
// 	if (!Array.isArray(customers)) {
// 		customers = customers ? [customers] : [];
// 	}

// 	const empty = {
// 		party_name: "",
// 		party_name_ar: "",
// 		tax_id: "",
// 		address_en: "",
// 		address_ar: "",
// 	};

// 	if (customers.length !== 1) {
// 		frappe.query_report.set_filter_value(empty);
// 		return;
// 	}

// 	const cust = await frappe.db.get_doc("Customer", customers[0]);

// 	// Primary address, else first address linked to the customer
// 	let address_name = cust.customer_primary_address;
// 	if (!address_name) {
// 		const linked = await frappe.db.get_list("Address", {
// 			filters: [
// 				["Dynamic Link", "link_doctype", "=", "Customer"],
// 				["Dynamic Link", "link_name", "=", cust.name],
// 			],
// 			fields: ["name"],
// 			order_by: "is_primary_address desc, modified desc",
// 			limit: 1,
// 		});
// 		address_name = linked.length ? linked[0].name : null;
// 	}

// 	const addr = address_name ? await frappe.db.get_doc("Address", address_name) : null;

// 	// One call with an object = one report refresh
// 	frappe.query_report.set_filter_value({
// 		party_name: cust.customer_name || cust.name,
// 		party_name_ar: cust.custom_customer_name_in_arabic || cust.zatca_customer_name_in_arabic || "",
// 		tax_id: cust.tax_id || "",
// 		address_en: csa_address_en(addr),
// 		address_ar: csa_address_ar(addr),
// 	});
// }

// // ------------------------------------------------------------
// // Force Print / PDF to always use the bilingual template.
// // Frappe falls back to the default "print_grid" (title + list of
// // filters) when "Pick Columns" is ticked or html_format is lost.
// // ------------------------------------------------------------
// function csa_force_print_template(report) {
// 	if (!report || report.__csa_print_patched) return;
// 	report.__csa_print_patched = true;

// 	const lock_template = () => {
// 		if (!report.report_settings) return;
// 		Object.defineProperty(report.report_settings, "html_format", {
// 			get: () => CSA_PRINT_HTML,
// 			set: () => {},
// 			configurable: true,
// 		});
// 	};

// 	const clean_settings = (s) => {
// 		s = Object.assign({}, s || {});
// 		delete s.columns; // "columns" makes Frappe use print_grid
// 		return s;
// 	};

// 	if (typeof report.print_report === "function") {
// 		const orig_print = report.print_report.bind(report);
// 		report.print_report = function (print_settings) {
// 			lock_template();
// 			return orig_print(clean_settings(print_settings));
// 		};
// 	}

// 	if (typeof report.pdf_report === "function") {
// 		const orig_pdf = report.pdf_report.bind(report);
// 		report.pdf_report = function (print_settings) {
// 			lock_template();
// 			return orig_pdf(clean_settings(print_settings));
// 		};
// 	}

// 	lock_template();
// }

// // ------------------------------------------------------------
// // Report definition
// // ------------------------------------------------------------
// frappe.query_reports["Customer Statement of Account"] = {
// 	// Always use our bilingual print template.
// 	get html_format() {
// 		return CSA_PRINT_HTML;
// 	},
// 	set html_format(v) {},

// 	onload: function (report) {
// 		csa_force_print_template(report);

// 		// Fill details if the report opens with a customer already selected
// 		if (report.get_filter_value("party")) {
// 			csa_set_customer_details();
// 		}
// 	},

// 	filters: [
// 		{
// 			fieldname: "company",
// 			label: __("Company"),
// 			fieldtype: "Link",
// 			options: "Company",
// 			default: frappe.defaults.get_user_default("Company"),
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "from_date",
// 			label: __("From Date"),
// 			fieldtype: "Date",
// 			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "to_date",
// 			label: __("To Date"),
// 			fieldtype: "Date",
// 			default: frappe.datetime.get_today(),
// 			reqd: 1,
// 		},
// 		{
// 			fieldname: "party",
// 			label: __("Customer"),
// 			fieldtype: "Link",
// 			options: "Customer",
// 			get_data: function (txt) {
// 				return frappe.db.get_link_options("Customer", txt, {
// 					company: frappe.query_report.get_filter_value("company"),
// 				});
// 			},
// 			on_change: function () {
// 				csa_set_customer_details();
// 			},
// 		},

// 		// ---- Hidden filters used by the print format ----
// 		{ fieldname: "party_name", label: __("Customer Name"), fieldtype: "Data", hidden: 1 },
// 		{ fieldname: "party_name_ar", label: __("Customer Name (Arabic)"), fieldtype: "Data", hidden: 1 },
// 		{ fieldname: "tax_id", label: __("Tax ID"), fieldtype: "Data", hidden: 1 },
// 		{ fieldname: "address_en", label: __("Address"), fieldtype: "Data", hidden: 1 },
// 		{ fieldname: "address_ar", label: __("Address (Arabic)"), fieldtype: "Data", hidden: 1 },

// 		{
// 			fieldname: "categorize_by",
// 			label: __("Categorize By"),
// 			fieldtype: "Select",
// 			options: [
// 				"",
// 				{ label: __("Categorize by Voucher"), value: "Categorize by Voucher" },
// 				{ label: __("Categorize by Voucher (Consolidated)"), value: "Categorize by Voucher (Consolidated)" },
// 				{ label: __("Categorize by Account"), value: "Categorize by Account" },
// 			],
// 			default: "Categorize by Voucher (Consolidated)",
// 		},
// 		{
// 			fieldname: "presentation_currency",
// 			label: __("Currency"),
// 			fieldtype: "Select",
// 			options: erpnext.get_presentation_currency_list(),
// 		},
// 		{
// 			fieldname: "include_dimensions",
// 			label: __("Consider Accounting Dimensions"),
// 			fieldtype: "Check",
// 			default: 1,
// 		},
// 		{
// 			fieldname: "ignore_cr_dr_notes",
// 			label: __("Ignore System Generated Credit / Debit Notes"),
// 			fieldtype: "Check",
// 		},
// 		{
// 			fieldname: "show_remarks",
// 			label: __("Show Remarks"),
// 			fieldtype: "Check",
// 		},
// 	],
// };
const CSA_PRINT_HTML = `
<!-- Modified on 08-10-2026 : bilingual customer name / address / VAT header -->
<!-- Address is optional: shown only when available -->

<style>

body,
html {
    margin-top: 10;
    padding: 0;
    width: 100%;
    height: auto;
    font-family: Arial, sans-serif;
}

.title-letter-spacing {
    letter-spacing: .2rem;
}

/* ---------- Customer header (English left / Arabic right) ---------- */
.customer-details {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    line-height: 1.35;
    margin: 6px 0 10px 0;
}
.customer-details td {
    border: none !important;
    padding: 0 !important;
    vertical-align: top;
    width: 50%;
}
.customer-details p {
    margin: 0 0 2px 0;
}
.customer-details .field-label {
    font-weight: bold;
}
.customer-details .customer-en {
    text-align: left;
    direction: ltr;
}
.customer-details .customer-ar {
    text-align: right;
    direction: rtl;
}
.customer-details .ltr-value,
.customer-details .num {
    direction: ltr;
    unicode-bidi: embed;
}

@media print {

    @page {
        size: A4;
        margin-top: 10mm;
    }

    .page-break {
        page-break-before: always;
        margin-top: 10mm;
    }

    thead {
        display: table-header-group;
    }

    tfoot {
        display: table-footer-group;
    }

    th,
    td {
        padding: 1px;
        border: 1px solid black;
    }

    .customer-details td {
        border: none !important;
        padding: 0 !important;
    }

    .no-print {
        display: none !important;
    }
}

</style>

<br>

<div style="font-family:Arial">

{%
var show_po_column = false;

if(!filters.party){
    show_po_column = true;
}else{
    for(var x=0; x<data.length; x++){
        if(data[x].po_no || data[x].remarks){
            show_po_column = true;
            break;
        }
    }
}

var single_customer = filters.party && (!Array.isArray(filters.party) || filters.party.length == 1);

/* Customer header details are attached by the .py to the first row */
var cust = {};
var all_rows = (typeof original_data !== "undefined" && original_data && original_data.length) ? original_data : data;
for (var c = 0; c < all_rows.length; c++) {
    if (all_rows[c] && all_rows[c].cust_name !== undefined) { cust = all_rows[c]; break; }
}

var cust_name = cust.cust_name || filters.party_name || (Array.isArray(filters.party) ? filters.party[0] : filters.party) || "";
var cust_tax_id = cust.cust_tax_id || filters.tax_id || "";
var cust_name_ar = cust.cust_name_ar || filters.party_name_ar || "";
var cust_address_en = cust.cust_address_en || filters.address_en || "";
var cust_address_ar = cust.cust_address_ar || filters.address_ar || "";
%}

<div>

<div style="text-align:center; font-size:15px; line-height:1.4; letter-spacing:0;">
    <div style="font-weight:bold; font-size:18px; margin-bottom:4px;">
        {%= __("STATEMENT OF ACCOUNTS") %}
    </div>

    {% if (!single_customer) { %}
        {%= __("All Customers ") %}<br>
    {% } %}
</div>

<div style="text-align:center; font-size:13px;">
    <b>
    {%= __("{0} to {1}", [
        frappe.datetime.str_to_user(filters.from_date),
        frappe.datetime.str_to_user(filters.to_date)
    ]) %}
    </b>
</div>


{% if (single_customer) { %}

<table class="customer-details">
    <tr>

        <!-- CUSTOMER - ENGLISH (LEFT) -->
        <td class="customer-en">

            <p>
                <span class="field-label">Client / Company:</span>
                {%= cust_name %}
            </p>

            {% if (cust_address_en) { %}
            <p>
                <span class="field-label">Address:</span>
                {%= cust_address_en %}
            </p>
            {% } %}

            {% if (cust_tax_id) { %}
            <p>
                <span class="field-label">VAT. No.:</span>
                {%= cust_tax_id %}
            </p>
            {% } %}

        </td>

        <!-- CUSTOMER - ARABIC (RIGHT) -->
        <td class="customer-ar">

            <p>
                <span class="field-label">العميل / الشركة:</span>
                {% if (cust_name_ar) { %}
                    {%= cust_name_ar %}
                {% } else { %}
                    <span class="ltr-value">{%= cust_name %}</span>
                {% } %}
            </p>

            {% if (cust_address_ar) { %}
            <p>
                <span class="field-label">العنوان:</span>
                {%= cust_address_ar %}
            </p>
            {% } %}

            {% if (cust_tax_id) { %}
            <p>
                <span class="field-label">الرقم الضريبي:</span>
                <span class="ltr-value">{%= cust_tax_id %}</span>
            </p>
            {% } %}

        </td>

    </tr>
</table>

{% } else { %}
<br>
{% } %}

</div>


<table style="width:100%; font-size:11px">

<thead>

<tr class="title-letter-spacing" style="text-align:center; font-weight:bold">

<td style="border:1.5px solid black; width:7em">
{%= __("Date").toLocaleUpperCase() %}
</td>

<td style="border:1.5px solid black">
{%= __("Particulars").toLocaleUpperCase() %}
</td>

{% if(show_po_column) { %}
<td style="border:1.5px solid black">
{%= __("Remarks").toLocaleUpperCase() %}
</td>
{% } %}

<td style="border:1.5px solid black; width:9em">
{%= __("Debit").toLocaleUpperCase() %}
</td>

<td style="border:1.5px solid black; width:9em">
{%= __("Credit").toLocaleUpperCase() %}
</td>

<td style="border:1.5px solid black; width:10.2em">
{%= __("Balance").toLocaleUpperCase() %}
</td>

</tr>

</thead>

<tbody>

{% for(var i=0, l=data.length; i<l; i++) { %}

<tr style="border-bottom:1px solid black">

{% if(data[i].posting_date) { %}

<td style="text-align:center; border:1px dotted black">
{%= frappe.datetime.str_to_user(data[i].posting_date) %}
</td>

<td style="border-right:1px dotted black">

{%= data[i].voucher_type %} {%= data[i].voucher_no %}

{% if(!(filters.party || filters.account)) { %}
{%= data[i].party || data[i].account %}
{% } %}

<br>

{% if(data[i].bill_no) { %}
{%= __("Supplier Invoice No") %}: {%= data[i].bill_no %}
{% } %}

</td>


{% if(show_po_column) { %}

<td style="border-right:1px dotted black; font-size:10px">

<!-- Sales Invoice PO -->

{% if(data[i].po_no) { %}

{%= __("Remarks") %}:
{%= __("Customer order against") %}
{%= data[i].po_no %}
{%= __("dated") %}
{%= frappe.datetime.str_to_user(data[i].po_date) %}

{% } %}


<!-- Payment Entry reference -->

{% if(data[i].voucher_type == "Payment Entry") { %}

{%= __("Remarks") %}:
{%= __("Customer against") %}
{%= data[i].reference_no || "" %}
{%= __("dated") %}
{%= data[i].reference_date ? frappe.datetime.str_to_user(data[i].reference_date) : "" %}

{% } %}


{% if(data[i].remarks) { %}
<br>
{%= data[i].remarks %}
{% } %}

</td>

{% } %}


<!-- DEBIT COLUMN -->

<td style="text-align:right; border-right:1px dotted black">

{% if(data[i].debit || data[i].debit == 0) { %}
{%= format_currency(data[i].debit, filters.presentation_currency) %}
{% } %}

</td>


<!-- CREDIT COLUMN -->

<td style="text-align:right; border-right:1px dotted black">

{% if(data[i].credit || data[i].credit == 0) { %}
{%= format_currency(data[i].credit, filters.presentation_currency) %}
{% } %}

</td>


{% } else { %}


<td style="text-align:center; border:1px dotted black">

{% if(i == 0) { %}
{%= frappe.datetime.str_to_user(filters.from_date) %}
{% } %}

</td>


<td style="text-align:left; border-right:1px dotted black">
<b>

{% if(i == l-2) { %}
{%= __("Total") %}
{% } else { %}

{% if(i == l-1) { %}
{%= __("Closing [Opening + Total] ") %}
{% } else { %}
{%= frappe.format(data[i].account, {fieldtype: "Link"}) || "&nbsp;" %}
{% } %}

{% } %}

</b>
</td>


{% if(show_po_column) { %}
<td style="border-right:1px dotted black"></td>
{% } %}


<!-- OPENING / TOTAL DEBIT -->

<td style="text-align:right; border-right:1px dotted black">

{% if(data[i].debit || data[i].debit == 0) { %}
{%= format_currency(data[i].debit, filters.presentation_currency) %}
{% } else { %}
0
{% } %}

</td>


<!-- OPENING / TOTAL CREDIT -->

<td style="text-align:right; border-right:1px dotted black">

{% if(data[i].credit || data[i].credit == 0) { %}
{%= format_currency(data[i].credit, filters.presentation_currency) %}
{% } else { %}
0
{% } %}

</td>

{% } %}


<!-- BALANCE -->

{% if(i == l-1) { %}

<td style="text-align:right; font-weight:bold; border-right:1px dotted black">

{%= format_currency(data[i].balance, filters.presentation_currency) %}

{% if(data[i].balance < 0){ %}Cr{% } %}
{% if(data[i].balance > 0){ %}Dr{% } %}

</td>

{% } else { %}

<td style="text-align:right; border-right:1px dotted black">

{% if(data[i].balance || data[i].balance == 0) { %}
{%= format_currency(data[i].balance, filters.presentation_currency) %}
{% } else { %}
0
{% } %}

</td>

{% } %}

</tr>

{% } %}

</tbody>

</table>


<p class="text-right text-muted">

{%= __("Printed on {0}",
[frappe.datetime.str_to_user(frappe.datetime.get_datetime_as_string())]) %}

</p>

</div>

`;

// ------------------------------------------------------------
// Helpers: build English / Arabic address HTML from an Address doc
// ------------------------------------------------------------
function csa_esc(v) {
	return frappe.utils.escape_html(v || "");
}

function csa_address_en(a) {
	if (!a) return "";
	const building_no = a.custom_building_number || a.building_number || "";
	const lines = [];

	if (a.address_line1) lines.push(csa_esc(a.address_line1));
	if (a.address_line2) lines.push(csa_esc(a.address_line2));

	if (building_no || a.city || a.pincode) {
		let city_line = "";
		if (building_no) city_line += "Building No. " + csa_esc(building_no) + ", ";
		city_line += csa_esc(a.city);
		if (a.pincode) city_line += " " + csa_esc(a.pincode);
		lines.push(city_line.trim().replace(/,$/, ""));
	}

	if (a.country) lines.push(csa_esc(a.country));
	return lines.join("<br>");
}

function csa_address_ar(a) {
	if (!a) return "";
	const building_no = a.custom_building_number || a.building_number || "";
	const line1 = a.custom_address_line_1_in_arabic || a.address_line1 || "";
	const line2 = a.custom_address_line_2_in_arabic || a.address_line2 || "";
	const city = a.custom_city_in_arabic || a.city || "";
	const country = a.country === "Saudi Arabia" ? "المملكة العربية السعودية" : a.country || "";
	const lines = [];

	if (line1) lines.push(csa_esc(line1));
	if (line2) lines.push(csa_esc(line2));

	if (building_no || city || a.pincode) {
		let city_line = "";
		if (building_no) city_line += 'رقم المبنى <span class="num">' + csa_esc(building_no) + "</span>، ";
		city_line += csa_esc(city);
		if (a.pincode) city_line += ' <span class="num">' + csa_esc(a.pincode) + "</span>";
		lines.push(city_line.trim().replace(/،$/, ""));
	}

	if (country) lines.push(csa_esc(country));
	return lines.join("<br>");
}

// ------------------------------------------------------------
// Load customer + address and store in hidden filters (for print)
// Address is optional: any failure just leaves it blank (no error popup)
// ------------------------------------------------------------
async function csa_set_customer_details() {
	let customers = frappe.query_report.get_filter_value("party");

	// Always normalize to array
	if (!Array.isArray(customers)) {
		customers = customers ? [customers] : [];
	}

	const details = {
		party_name: "",
		party_name_ar: "",
		tax_id: "",
		address_en: "",
		address_ar: "",
	};

	if (customers.length !== 1) {
		frappe.query_report.set_filter_value(details);
		return;
	}

	try {
		const cust = await frappe.db.get_doc("Customer", customers[0]);

		details.party_name = cust.customer_name || cust.name;
		details.party_name_ar =
			cust.custom_customer_name_in_arabic || cust.zatca_customer_name_in_arabic || "";
		details.tax_id = cust.tax_id || "";

		try {
			let address_name = cust.customer_primary_address;

			if (address_name && !(await frappe.db.exists("Address", address_name))) {
				address_name = null;
			}

			if (!address_name) {
				const r = await frappe.call({
					method: "frappe.contacts.doctype.address.address.get_default_address",
					args: { doctype: "Customer", name: cust.name },
					freeze: false,
				});
				address_name = r && r.message;
			}

			if (address_name) {
				const addr = await frappe.db.get_doc("Address", address_name);
				details.address_en = csa_address_en(addr);
				details.address_ar = csa_address_ar(addr);
			}
		} catch (e) {
			console.warn("Customer Statement: address not loaded", e);
		}
	} catch (e) {
		console.warn("Customer Statement: customer details not loaded", e);
	}

	// One call with an object = one report refresh
	frappe.query_report.set_filter_value(details);
}

// ------------------------------------------------------------
// Force Print / PDF to always use the bilingual template.
// Frappe falls back to the default "print_grid" (title + list of
// filters) when "Pick Columns" is ticked or html_format is lost.
// ------------------------------------------------------------
function csa_force_print_template(report) {
	if (!report || report.__csa_print_patched) return;
	report.__csa_print_patched = true;

	const lock_template = () => {
		if (!report.report_settings) return;
		Object.defineProperty(report.report_settings, "html_format", {
			get: () => CSA_PRINT_HTML,
			set: () => {},
			configurable: true,
		});
	};

	const clean_settings = (s) => {
		s = Object.assign({}, s || {});
		delete s.columns; // "columns" makes Frappe use print_grid
		return s;
	};

	if (typeof report.print_report === "function") {
		const orig_print = report.print_report.bind(report);
		report.print_report = function (print_settings) {
			lock_template();
			return orig_print(clean_settings(print_settings));
		};
	}

	if (typeof report.pdf_report === "function") {
		const orig_pdf = report.pdf_report.bind(report);
		report.pdf_report = function (print_settings) {
			lock_template();
			return orig_pdf(clean_settings(print_settings));
		};
	}

	lock_template();
}

// ------------------------------------------------------------
// Report definition
// ------------------------------------------------------------
frappe.query_reports["Customer Statement of Account"] = {
	// Always use our bilingual print template.
	get html_format() {
		return CSA_PRINT_HTML;
	},
	set html_format(v) {},

	onload: function (report) {
		csa_force_print_template(report);

		// Fill details if the report opens with a customer already selected
		if (report.get_filter_value("party")) {
			csa_set_customer_details();
		}
	},

	filters: [
		{
			fieldname: "company",
			label: __("Company"),
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
			reqd: 1,
		},
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "party",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			get_data: function (txt) {
				return frappe.db.get_link_options("Customer", txt, {
					company: frappe.query_report.get_filter_value("company"),
				});
			},
			on_change: function () {
				csa_set_customer_details();
			},
		},

		// ---- Hidden filters used by the print format (all optional) ----
		{ fieldname: "party_name", label: __("Customer Name"), fieldtype: "Data", hidden: 1 },
		{ fieldname: "party_name_ar", label: __("Customer Name (Arabic)"), fieldtype: "Data", hidden: 1 },
		{ fieldname: "tax_id", label: __("Tax ID"), fieldtype: "Data", hidden: 1 },
		{ fieldname: "address_en", label: __("Address"), fieldtype: "Data", hidden: 1 },
		{ fieldname: "address_ar", label: __("Address (Arabic)"), fieldtype: "Data", hidden: 1 },

		{
			fieldname: "categorize_by",
			label: __("Categorize By"),
			fieldtype: "Select",
			options: [
				"",
				{ label: __("Categorize by Voucher"), value: "Categorize by Voucher" },
				{ label: __("Categorize by Voucher (Consolidated)"), value: "Categorize by Voucher (Consolidated)" },
				{ label: __("Categorize by Account"), value: "Categorize by Account" },
			],
			default: "Categorize by Voucher (Consolidated)",
		},
		{
			fieldname: "presentation_currency",
			label: __("Currency"),
			fieldtype: "Select",
			options: erpnext.get_presentation_currency_list(),
		},
		{
			fieldname: "include_dimensions",
			label: __("Consider Accounting Dimensions"),
			fieldtype: "Check",
			default: 1,
		},
		{
			fieldname: "ignore_cr_dr_notes",
			label: __("Ignore System Generated Credit / Debit Notes"),
			fieldtype: "Check",
		},
		{
			fieldname: "show_remarks",
			label: __("Show Remarks"),
			fieldtype: "Check",
		},
	],
};