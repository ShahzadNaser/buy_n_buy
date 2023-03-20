# Copyright (c) 2023, Shahzad Naser and contributors
# For license information, please see license.txt

import frappe
from frappe import _



def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)

	return columns, data
def get_data(filters):
	condition = " 1=1 "
	if filters.get("posting_date"):
		condition += " AND sle.posting_date <= '{}'".format(filters.get("posting_date"))

	if filters.get("warehouse"):
		condition += " AND sle.warehouse = '{}'".format(filters.get("warehouse"))

	if filters.get("item_code"):
		condition += " AND sle.item_code = '{}'".format(filters.get("item_code"))

	if filters.get("item_group"):
		condition += " AND item.item_group = '{}'".format(filters.get("item_group"))

	return frappe.db.sql(""" 
		SELECT 
			sle.warehouse,
			sle.item_code,
			item.item_name,
			item.item_group,
			sle.batch_no,
			sle.company,
			item.stock_uom,
			SUM(sle.actual_qty) as bal_qty,
			sle.incoming_rate,
			sle.incoming_rate * SUM(sle.actual_qty) as stock_value,
			item_def.conversion_factor as packing,
			ROUND(SUM(sle.actual_qty)/item_def.conversion_factor,3) as ctn,
			ROUND((item_def.cbm_1*item_def.cbm_2*item_def.cbm_3)*((SUM(sle.actual_qty)/item_def.conversion_factor)/1000000),3) as tcbm,
			ROUND(item.weight_per_unit*SUM(sle.actual_qty)) as tw
		FROM
			`tabStock Ledger Entry` sle
		LEFT JOIN
			`tabItem` item
			ON
				sle.item_code = item.name 
		LEFT JOIN
			`tabUOM Conversion Detail` item_def
			ON
				sle.item_code = item_def.parent and item_def.uom = 'Box'
		WHERE
  			{}
		GROUP BY sle.item_code , sle.warehouse

		ORDER BY sle.item_code              
	""".format(condition),as_dict=True,debug=True)


def get_columns():
	"""return columns"""
	columns = [
		{
			"label": _("Item"),
			"fieldname": "item_code",
			"fieldtype": "Link",
			"options": "Item",
			"width": 100,
		},
		{"label": _("Item Name"), "fieldname": "item_name", "width": 150},
		{
			"label": _("Item Group"),
			"fieldname": "item_group",
			"fieldtype": "Link",
			"options": "Item Group",
			"width": 100,
		},
  		{
			"label": _("CARTON MARK"),
			"fieldname": "batch_no",
			"fieldtype": "Link",
			"options": "Batch",
			"width": 100,
		},
		{
			"label": _("PACKING"),
			"fieldname": "packing",
			"fieldtype": "Int",
			"width": 100,
		},
  		{
			"label": _("CTN"),
			"fieldname": "ctn",
			"fieldtype": "Float",
			"width": 100,
		},
		{
			"label": _("Warehouse"),
			"fieldname": "warehouse",
			"fieldtype": "Link",
			"options": "Warehouse",
			"width": 100,
		},
		{
			"label": _("Stock UOM"),
			"fieldname": "stock_uom",
			"fieldtype": "Link",
			"options": "UOM",
			"width": 90,
		},
		{
			"label": _("Balance Qty"),
			"fieldname": "bal_qty",
			"fieldtype": "Float",
			"width": 100,
			"convertible": "qty",
		},
		{
			"label": _("Rate"),
			"fieldname": "incoming_rate",
			"fieldtype": "Currency",
			"width": 100,
			"options": "currency",
		},
		{
			"label": _("Balance Value"),
			"fieldname": "stock_value",
			"fieldtype": "Currency",
			"width": 100,
			"options": "currency",
		},
  		{
			"label": _("T.CBM"),
			"fieldname": "tcbm",
			"fieldtype": "Float",
			"width": 100,
		},  		
    	{
			"label": _("T.WEIGHT"),
			"fieldname": "tw",
			"fieldtype": "Float",
			"width": 100,
		},  
  		{
			"label": _("Company"),
			"fieldname": "company",
			"fieldtype": "Link",
			"options": "Company",
			"width": 100,
		}
	]

	return columns

