import frappe

@frappe.whitelist()
def get_item_details(item_code=None):
    print(item_code)
    if not item_code:
        return False

    return frappe.db.get_value("UOM Conversion Detail",{"parent":item_code,"uom":"Box"},["conversion_factor","cbm_1","cbm_2","cbm_3"],as_dict=True)

@frappe.whitelist()
def ping():
    return "Pong"

@frappe.whitelist()
def make_new_batch(doc,method):
    for item in doc.get("items"):
        if not frappe.db.exists("Batch",item.get("batch_no")):
            batch = frappe.new_doc("Batch")
            batch.batch_id = item.get("batch_no")
            batch.item = item.get("item_code")
            batch.flags.ignore_permissions = 1
            batch.insert()


