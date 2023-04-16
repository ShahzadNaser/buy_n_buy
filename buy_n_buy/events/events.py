import frappe
from erpnext.stock.doctype.batch.batch import get_batch_no

@frappe.whitelist()
def get_item_details(item_code=None, warehouse=None):
    if not item_code:
        return False
    result = frappe.db.get_value("UOM Conversion Detail",{"parent":item_code,"uom":"Box"},["conversion_factor as fac","cbm_1","cbm_2","cbm_3"],as_dict=True)
    where = " item_code = '{}'".format(item_code)
    if warehouse:
        result["batch_no"] = get_batch_no(item_code,warehouse,1,throw=False)
        from erpnext.stock.get_item_details import get_bin_details
        where += " and warehouse = '{}'".format(warehouse)
    result["actual_qty"] = 0

    query_res = frappe.db.sql(""" SELECT SUM(actual_qty) as actual_qty from `tabBin` where %s """%where,as_dict=True)
    if query_res:
        result["actual_qty"] = query_res[0]["actual_qty"]

    return result

@frappe.whitelist()
def ping():
    return "Pong"

@frappe.whitelist()
def make_new_batch(doc,method):
    for item in doc.get("items"):
        if not frappe.db.exists("Batch",item.get("batch_number")):
            batch = frappe.new_doc("Batch")
            batch.batch_id = item.get("batch_number")
            batch.item = item.get("item_code")
            batch.flags.ignore_permissions = 1
            batch.insert()


