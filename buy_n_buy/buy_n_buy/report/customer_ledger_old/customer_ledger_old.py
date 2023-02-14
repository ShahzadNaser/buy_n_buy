# Copyright (c) 2022, Shahzad Naser and contributors
# For license information, please see license.txt

import frappe
from frappe import _, scrub
from frappe.utils import getdate, nowdate, flt


def execute(filters=None):
	data = []
	columns = [
		{
			"label": _("Date"),
			"fieldtype": "Date",
			"fieldname": "posting_date",
			"width": 100,
		},
		{
			"label": _("Reference No."),
			"fieldtype": "Data",
			"fieldname": "so",
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


def get_gl_entries(filters={} ):
	gl_entries = frappe.db.sql(
		"""
		select
			sum(gle.debit) - (sum(gle.credit) + sum(gle.is_opening)) as opening_balance
		from `tabGL Entry` gle
		where
			gle.docstatus < 2 and gle.is_cancelled = 0 and gle.party_type='customer' and gle.party = '{}' 
			and gle.posting_date < '{}'
		group by gle.party
		
	""".format(filters.get("customer"), filters.get("from_date")),
		as_dict=True
	)

	if gl_entries:
		return gl_entries[0].get("opening_balance")
	return 0

def get_date(filters):
	opening = get_gl_entries(filters)
	closing = flt(opening)
	data = []
	opening_row = frappe._dict({
		"posting_date": "",
		"so": 'Opening Balance',
		"item": "",
		"qty": "",
		"rate": "",
		"amount": "",
		"debit": "",
		"credit":"",
		"balance":opening
	})
	data.append(opening_row)

	sales_orders = get_sales_orders(filters)
	temp_orders = []
	# outsanding_orders = get_outstanding_invoices(filters)
	payments = get_payments(filters)

	transaction =  sorted(sales_orders + payments, key=lambda d: d['posting_date']) 

	for row in transaction:
		if row.get("sales_order") not in temp_orders:
			closing = closing +(flt(row.get("debit") or 0) - flt(row.get("credit") or 0))

		data.append(
			frappe._dict({
				"posting_date": row.get("posting_date") if row.get("sales_order") not in temp_orders else "",
				"so": row.get("sales_order") if row.get("sales_order") not in temp_orders else "",
				"item": row.get("item_code") or "",
				"qty": row.get("qty") or "",
				"rate": row.get("rate") or "",
				"amount": row.get("amount") or "",
				"debit": row.get("debit") if row.get("sales_order") not in temp_orders else "",
				"credit":row.get("credit") if row.get("sales_order") not in temp_orders else "",
				"balance": closing if row.get("sales_order") not in temp_orders else ""
			})
		)		
		if row.get("sales_order") not in temp_orders:
			temp_orders.append(row.get("sales_order"))


	closing_row = frappe._dict({
		"posting_date": "",
		"so": "Closing Balance",
		"item": "",
		"qty": "",
		"rate": "",
		"amount": "",
		"debit": "",
		"credit":"",
		"balance":closing
	})

	data.append(closing_row)
 
	return data

def new_so_row(posting_date, so, credit, debit, balance):
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

def get_sales_orders(filters):
    orders = frappe.db.sql(
	"""
		SELECT 
			so.name as sales_order,
			so.transaction_date as posting_date,
			soi.item_code,
			soi.item_name,
			soi.qty,
			soi.rate,
			soi.amount,
			so.rounded_total as debit,
			0 as credit
		FROM
			`tabSales Order` so
		LEFT JOIN
			`tabSales Order Item` soi
			ON 
				soi.parent = so.name
		WHERE
			so.customer = '{}' AND so.transaction_date between '{}' AND '{}' and so.docstatus  < 2
		GROUP BY
			so.name, soi.name
		ORDER BY 
			so.transaction_date, so.name asc		
	""".format(filters.get("customer"), filters.get("from_date"),filters.get("to_date")),
		as_dict=True
	)
    return orders

def get_outstanding_invoices(filters):
    orders = frappe.db.sql(
	"""
		SELECT 
			soi.sales_order,
			si.outstanding_amount
		FROM
			`tabSales Invoice` si
		INNER JOIN
			`tabSales Invoice Item` soi
			ON 
				si.name = soi.parent
		WHERE 
			si.customer = '{}' and si.posting_date >= '{}'		
	""".format(filters.get("customer"), filters.get("from_date")),
		as_dict=True
	)
    outstanding_balances = frappe._dict({})
    for row in orders:
        outstanding_balances[row.get("sales_order")] = flt(row.get("outstanding_amount") or 0)
    return outstanding_balances

def get_payments(filters):
    return frappe.db.sql(
	"""
		SELECT
			pe.name as sales_order,
			pe.posting_date ,
			0 as debit,
			pe.paid_amount as credit
		FROM
			`tabPayment Entry` pe
		WHERE
			pe.party = '{}' AND pe.posting_date between '{}' AND '{}' and pe.docstatus  = 1
		ORDER BY
			posting_date asc		
	""".format(filters.get("customer"), filters.get("from_date"),filters.get("to_date")),
		as_dict=True
	)
