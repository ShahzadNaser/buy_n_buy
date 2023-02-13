# Copyright (c) 2022, Shahzad Naser and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt
from erpnext.accounts.report.general_ledger.general_ledger import execute as get_gl

def execute(filters=None):
	data = []
	columns = [
		{
			"label": _("Date"),
			"fieldtype": "Date",
			"fieldname": "posting_date",
			"width": 100,
		},
		{"label": _("Voucher Type"), "fieldname": "voucher_type", "width": 120},
		{
			"label": _("Voucher No"),
			"fieldname": "voucher_no",
			"fieldtype": "Dynamic Link",
			"options": "voucher_type",
			"width": 180,
		},
		{
			"label": _("Item"),
			"fieldtype": "Link",
			"fieldname": "item",
			"options": "Item",
			"width": 180,
		},
		{
			"label": _("QTY"),
			"fieldtype": "Float",
			"fieldname": "qty",
			"width": 80,
		},
		{
			"label": _("Rate"),
			"fieldtype": "Currency",
			"fieldname": "rate",
			"width": 120,
		},
		{
			"label": _("Amount"),
			"fieldtype": "Currency",
			"fieldname": "amount",
			"width": 120,
		},
		{
			"label": _("Debit"),
			"fieldtype": "Currency",
			"fieldname": "debit",
			"width": 140,
		},
		{
			"label": _("Credit"),
			"fieldtype": "Currency",
			"fieldname": "credit",
			"width": 140,
		},
		{
			"label": _("Balance"),
			"fieldtype": "Currency",
			"fieldname": "balance",
			"width": 140,
		}
	]    
	data = get_date(filters)
	return columns, data

def get_date(filters):
	invoices = get_sales_invoices(filters)
	filters["group_by"] = "Group by Voucher (Consolidated)"
	filters["party_type"] = "Customer"
	filters["party"] = [filters.get("party")]
	data = []
	columns, tdata = get_gl(filters)
	for row in tdata:
		temp_row = frappe._dict({
			"posting_date": row.get("posting_date"),
			"voucher_type": row.get("account") if row.get("account") in ['Opening','Total','Closing (Opening + Total)'] else row.get("voucher_type"),
			"voucher_no":  row.get("voucher_no") or "",
			"item": "",
			"qty": "",
			"rate": "",
			"amount": "",
			"debit": row.get("debit"),
			"credit":row.get("credit"),
			"balance":row.get("balance")
		})
		data.append(temp_row)
		first = True
		if(row.get("voucher_no") and row.get("voucher_no") in invoices):
			for trow in invoices.get(row.get("voucher_no")) or []:
				print(trow)
			if first:
				child_row = temp_row
				child_row.update(trow)
			else:
				temp_row = frappe._dict({
					"posting_date": "",
					"voucher_type": "",
					"voucher_no":  "",
					"item": trow.get("item"),
					"qty": trow.get("qty"),
					"rate": trow.get("rate"),
					"amount": trow.get("amount"),
					"debit": "",
					"credit":"",
					"balance":""
				})
			data.append(child_row)
		else:
			data.append(temp_row) 
		print(data)
	return data

def new_si_row(posting_date, so, credit, debit, balance):
	return frappe._dict({
		"posting_date": posting_date,
		"so": so,
		"item": "",
		"qty": "",
		"rate": "",
		"amount": "",
		"debit": debit,
		"credit":credit,
		"balance":balance
	})

def get_sales_invoices(filters):
	invoices = frappe.db.sql(
	"""
		SELECT 
			s.name,
			si.item_code as item,
			si.qty,
			si.rate,
			s.grand_total as amount
		FROM
			`tabSales Invoice` s
		LEFT JOIN
			`tabSales Invoice Item` si
			ON 
				si.parent = s.name
		WHERE
			s.posting_date between '{}' AND '{}' and s.docstatus  = 1
		GROUP BY
			s.name, si.name
		ORDER BY 
			s.posting_date, s.name asc
	""".format(filters.get("from_date"),filters.get("to_date")),
		as_dict=True
	)
	invoices_dict = {}
	for row in invoices:
		if row.get("name") not in invoices_dict:
			invoices_dict[row.get("name")] = [row]
		else:
			invoices_dict[row.get("name")].append(row)
	return invoices_dict