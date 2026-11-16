# Claudion Add-ons

Extra reports and controls for ERPNext, built by [ERPGulf](https://erpgulf.com) for customers on the [Claudion](https://claudion.com) cloud.

The app name is `claudion_addons`. It needs ERPNext; everything below sits on top of standard ERPNext documents.

## What it adds

| Feature | Where you find it |
| --- | --- |
| [Customer Statement of Account](#customer-statement-of-account) | Reports, under the name *Customer Statement of Account* |
| [Cost Center, Project and Sales Team on Quotation](#cost-center-project-and-sales-team-on-quotation) | The Quotation form |
| [Purchase invoice date check, block or warn](#purchase-invoice-date-check) | *Claudion Add-on Settings* |

## Customer Statement of Account

A statement of one customer's account, or of all customers, for any period. It is built on ERPNext's General Ledger, so its figures always agree with the ledger.

**What it shows beyond the General Ledger**

- **Customer Name** beside the customer code.
- **The customer's order number and date** on each sales invoice line, taken from the invoice.
- **The payment reference and its date** on each payment line, taken from the payment entry.
- **A heading** above the table with the customer's name, tax ID and the period.

**Filters**

- Company, From Date and To Date (all required), and Customer.
- Categorize By: voucher, voucher consolidated, or account.
- Currency.
- Show Remarks: adds the remarks column.
- Ignore System Generated Credit / Debit Notes.
- Consider Accounting Dimensions.

**The printout**

Printing the report for a single customer gives a statement ready to send:

- The customer's details in **English and Arabic side by side**: name, address and VAT number. The Arabic name and address come from the customer's record; where there is no Arabic name, the English one is used.
- Columns for Date, Particulars, Debit, Credit and running Balance, with Remarks when *Show Remarks* is ticked.

**Who can run it:** Accounts User, Accounts Manager and Auditor.

## Cost Center, Project and Sales Team on Quotation

Standard ERPNext has these on Sales Order and Sales Invoice but not on Quotation, so they had to be filled in again at order time. This app adds them to Quotation:

- **Cost Center** and **Project**, in an *Accounting Dimensions* section.
- **Sales Team**, at the top of the *More Info* tab: the same table of sales persons, contribution percentages and incentives as on Sales Order.

**They carry forward.** When a Sales Order or a Sales Invoice is created from the quotation, the cost center, the project and the sales team are copied to it. From a Sales Order to its Sales Invoice they continue as ERPNext already does.

**Details**

- A customer's default sales team fills in on the quotation, as it does on a sales order.
- The same rules apply as on a sales order: a sales person cannot appear twice, and contributions must add up to 100%.
- *Contribution to Net Total* is worked out when the quotation is saved. Items whose *Grant Commission* is unticked on the item are left out of it, as on a sales order.
- Cost center and project are for the whole quotation. Quotation item rows have no cost center or project of their own.

The fields are created when the app is installed and checked again on every `bench migrate`.

## Purchase invoice date check

ERPNext refuses a purchase invoice whose posting date is earlier than the date of its purchase order. Some businesses need to allow it, for example when a purchase order is raised after the supplier's invoice has arrived.

*Claudion Add-on Settings* has one option, **Validate PO Date with PI Date**:

- **Ticked** (the default): the invoice is refused, as in standard ERPNext.
- **Not ticked**: the invoice is saved, with a warning listing the purchase orders concerned and their dates.

To provide this, the app replaces ERPNext's Purchase Invoice class with its own. Only the date check is changed.

## Installation

```bash
bench get-app https://github.com/ERPGulf/claudion-addons.git
bench --site your-site-name install-app claudion_addons
bench --site your-site-name migrate
```

Used on Frappe and ERPNext version 16.

## Support

- Email: [support@erpgulf.com](mailto:support@erpgulf.com)
- Website: [erpgulf.com](https://erpgulf.com)
- Cloud: [claudion.com](https://claudion.com)

## License

MIT. See [license.txt](license.txt).