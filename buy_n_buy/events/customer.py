import frappe

def before_save(doc, method):
    if doc.get("supplier"):
        if frappe.db.get_value("Customer",{"name":["!=",doc.get("name")],"supplier":doc.get("supplier")},"name"):
            frappe.throw("{} Supplier alreadly linked with another Customer".format(doc.get("supplier")))