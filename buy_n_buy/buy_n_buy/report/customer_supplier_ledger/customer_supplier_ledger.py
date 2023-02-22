# Copyright (c) 2023, Shahzad Naser and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data
# Copyright (c) 2022, Shahzad Naser and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt
from erpnext.accounts.report.general_ledger.general_ledger import execute as get_gl
from collections import ChainMap


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
			"label": _("Party Type"),
			"fieldtype": "Data",
			"fieldname": "party_type",
			"width": 100,
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
	data = get_data(filters)
	return columns, data

def get_data(filters):
	sinvoices = get_sales_invoices(filters)
	supplier = ""
	if filters.get("include_supplier"):
		supplier = frappe.db.get_value("Customer",filters.get("party"),"supplier") or ""
	purchase_invoices = get_purchase_invoices(filters, supplier)
	invoices = ChainMap(sinvoices, purchase_invoices) 
	filters["group_by"] = "Group by Voucher (Consolidated)"
	pi_filters = filters

	filters["party"] = [filters.get("party")]
 	
	data = []
	columns, tdata = get_gl(filters)
	print(tdata)
	pdata= [{}]

	if filters["party_type"] == "Customer" and supplier:
		pi_filters["party_type"] = "Supplier"
		pi_filters["party"] = [supplier]
		columns, pdata = get_gl(pi_filters)
	transactions = pdata + tdata
	sfirst = tdata[0]
	pfirst = pdata[0]
	opening_balance = {"debit":sfirst.get("balance") or 0,"credit":pfirst.get("balance") or 0,"balance":(sfirst.get("balance") or 0) - abs(pfirst.get("balance") or 0)}
	cur_balance = (sfirst.get("balance") or 0) - abs(pfirst.get("balance") or 0)
	closing_balance = {"debit":opening_balance.get("debit") or 0,"credit":opening_balance.get("credit") or 0,"balance":opening_balance.get("balance") or 0}

	transactions =  sorted(tdata + pdata, key=lambda d: d.get('posting_date') or getdate("2000-10-10") )
	data.append(
		frappe._dict({
			"posting_date":"",
			"voucher_type": "" ,
			"voucher_no":  "Opening",
			"item": "",
			"qty": "",
			"rate": "",
			"amount": "",
			"debit": opening_balance.get("debit"),
			"credit":opening_balance.get("credit"),
			"balance":opening_balance.get("balance")
		})
	)
	for row in transactions:
		if row.get("posting_date"):
			closing_balance["debit"] += row.get("debit")
			closing_balance["credit"] += row.get("credit")
			closing_balance["balance"] +=  (row.get("debit") - abs(row.get("credit")))

			temp_row = frappe._dict({
				"posting_date": row.get("posting_date"),
				"voucher_type": "" if row.get("account") in ['Opening','Total','Closing (Opening + Total)'] else row.get("voucher_type"),
				"voucher_no":  row.get("voucher_no") or row.get("account"),
				"party_type": row.get("party_type"),
				"item": "",
				"qty": "",
				"rate": "",
				"amount": "",
				"debit": row.get("debit"),
				"credit":row.get("credit"),
				"balance":closing_balance["balance"]
			})
			first = True
			if(row.get("voucher_no") and row.get("voucher_no") in invoices):
				for trow in invoices.get(row.get("voucher_no")) or []:
					if first:
						child_row = temp_row
						child_row.update(trow)
					else:
						child_row = frappe._dict({
							"posting_date": "",
							"voucher_type": "",
							"voucher_no":  "",
							"item": trow.get("item"),
							"qty": trow.get("qty"),
							"rate": trow.get("rate"),
							"amount": trow.get("qty") * trow.get("rate"),
							"debit": "",
							"credit":"",
							"balance":""
						})

					first = False

					data.append(child_row)
			else:
				data.append(temp_row) 
			print(closing_balance["balance"])
	data.append(
		frappe._dict({
			"posting_date":"",
			"voucher_type": "" ,
			"voucher_no":  "Closing",
			"item": "",
			"qty": "",
			"rate": "",
			"amount": "",
			"debit": closing_balance.get("debit"),
			"credit":closing_balance.get("credit"),
			"balance":closing_balance.get("balance")
		})
	)

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
			s.customer = '{}' and s.posting_date between '{}' AND '{}' and s.docstatus  = 1
		GROUP BY
			s.name, si.name
		ORDER BY 
			s.posting_date, s.name asc
	""".format(filters.get("party"),filters.get("from_date"),filters.get("to_date")),
		as_dict=True
	)
	invoices_dict = {}
	for row in invoices:
		if row.get("name") not in invoices_dict:
			invoices_dict[row.get("name")] = [row]
		else:
			invoices_dict[row.get("name")].append(row)
	return invoices_dict

def get_purchase_invoices(filters,supplier=""):
	invoices = frappe.db.sql(
	"""
		SELECT 
			p.name,
			pi.item_code as item,
			pi.qty,
			pi.rate,
			p.grand_total as amount
		FROM
			`tabPurchase Invoice` p
		LEFT JOIN
			`tabPurchase Invoice Item` pi
			ON 
				pi.parent = p.name
		WHERE
			p.posting_date between '{}' AND '{}' and p.docstatus  = 1
		GROUP BY
			p.name, pi.name
		ORDER BY 
			p.posting_date, p.name asc
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