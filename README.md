# Claudion Add-ons

Extra reports and controls for ERPNext, built by [ERPGulf](https://erpgulf.com) for customers on the [Claudion](https://claudion.com) cloud.

The app name is `claudion_addons`. It needs ERPNext; everything below sits on top of standard ERPNext documents.

## What it adds

| Feature | Where you find it |
| --- | --- |
| [Customer Statement of Account](#customer-statement-of-account) | Reports, under the name *Customer Statement of Account* |
| [Cost Center, Project and Sales Team on Quotation](#cost-center-project-and-sales-team-on-quotation) | The Quotation form |
| [Purchase invoice date check, block or warn](#purchase-invoice-date-check) | *Claudion Add-on Settings* |
| [Supplier Payment Request](#supplier-payment-request) | Its own document, *Supplier Payment Request* |

## Customer Statement of Account

A statement of one customer's account, or of all customers, for any period. It is built on ERPNext's General Ledger, so its figures always agree with the ledger.

**What it shows beyond the General Ledger**

- **Customer Name** beside the customer code.
- **The customer's order number and date** for each sales invoice, taken from the invoice. Shown on the printout, in the Remarks column.
- **The payment reference and its date** for each payment, taken from the payment entry. Shown on the printout, in the Remarks column.
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

- The customer's details in **English and Arabic side by side**: name, address and VAT number. The Arabic name and address come from the customer's record; where there is no Arabic name or address, the English one is used. The Arabic fields themselves are not created by this app.
- Columns for Date, Particulars, Debit, Credit and running Balance. A Remarks column is added when any invoice in the period has a customer order number, when *Show Remarks* is ticked, or when the statement is for all customers.

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

## Supplier Payment Request

One request for payments to several suppliers, approved together. After approval, draft Payment Entries are created from it, one per supplier row. The request itself posts nothing to the ledger.

**The request**

- Company, request date, the bank or cash account to pay from, and optionally a mode of payment and a reference.
- **Supplier Payments**: one row per supplier, with the amount. The supplier's payable account and current payable balance are shown for reference.
- Each row is either **On Account** (an unallocated payment, to be matched later with Payment Reconciliation) or **Against Invoices**.
- **Invoice Allocation**: for an Against Invoices supplier, the purchase invoices being paid and the amount against each. The invoices may add up to less than the row amount; the rest stays unallocated. They may not add up to more.

**Approval**

Approved means submitted. An approved request cannot be edited.

A starting workflow, *Supplier Payment Request Approval*, is created once when the feature first reaches a site: Draft, Pending Approval, Approved, Rejected, Cancelled, with Accounts User raising requests and Accounts Manager approving. After that the workflow belongs to the site. Change the approver roles, add levels or add amount limits in the Workflow itself; updates to this app never overwrite it. A site can also switch the workflow off and approve with the plain Submit button.

**Create Payment Entries**

The button appears on an approved request while any row has no payment entry yet. It is shown to users who are allowed to create Payment Entries.

- A dialog lists the rows. Untick the ones to leave for later; the posting date and the paid-from account can be changed for this run.
- One **draft** Payment Entry is created per ticked row. Nothing is submitted: the user reviews and submits each entry in the usual Payment Entry form.
- Invoice outstanding amounts are checked again at this moment, because they may have changed since approval.
- A row that fails is reported with the reason and does not stop the others. A row that already has an entry is never created twice.
- Where the request has no reference number, the request number is put on the draft as its reference, because ERPNext does not save a bank payment without one. Replace it with the real cheque or transfer reference before submitting.

**Each row shows where it stands**

| Entry Status | Meaning |
| --- | --- |
| Not Created | No payment entry yet |
| Draft Created | A draft payment entry is linked |
| Submitted | The payment entry has been submitted |

When a linked payment entry is cancelled, or a draft is deleted, the row goes back to *Not Created* so it can be created again. The Payment Entry carries a link back to its request.

**Rules**

- Once payment entries have been created from a request, the request can never be cancelled, even if those entries are later cancelled or deleted.
- A supplier that is disabled, or on hold for payments, is refused.
- A supplier can have several On Account rows but only one Against Invoices row. The same supplier with the same amount twice gives a warning.
- The paid-from account and the suppliers' payable accounts must be in the company currency. Payments across currencies are not supported.

**Who can do what** is set on each site and can differ from client to client:

| What | Where it is set | As installed |
| --- | --- | --- |
| Raise, approve, reject, cancel a request | The site's Workflow and Role Permission Manager | Accounts User raises; Accounts Manager approves and cancels |
| Create the payment entries | Create permission on Payment Entry | Whoever can create Payment Entries today |
| Which companies a user sees | User Permissions on Company | No restriction |

## Installation

```bash
bench get-app https://github.com/ERPGulf/claudion-addons.git
bench --site your-site-name install-app claudion_addons
bench --site your-site-name migrate
```

Used on Frappe and ERPNext version 16.

## For developers

Every feature keeps to its own folder under `claudion_addons/`, and `hooks.py` only wires them in:

| Folder | Feature |
| --- | --- |
| `quotation_fields/` | Cost Center, Project and Sales Team on Quotation |
| `purchase_invoice_date_check/` | Purchase invoice date check |
| `supplier_payment_request/` | Supplier Payment Request |
| `claudion_addons/` | *Claudion Add-on Settings* and the Customer Statement of Account report |

A new feature gets a new folder. It should not change the behaviour of a feature clients already use.

## Support

- Email: [support@erpgulf.com](mailto:support@erpgulf.com)
- Website: [erpgulf.com](https://erpgulf.com)
- Cloud: [claudion.com](https://claudion.com)

## License

MIT. See [license.txt](license.txt).