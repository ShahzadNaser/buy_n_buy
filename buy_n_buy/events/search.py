import frappe
from frappe import _
from frappe.desk.search import search_widget, build_for_autosuggest

# this is called by the Link Field
@frappe.whitelist()
def search_link(
	doctype,
	txt,
	query=None,
	filters=None,
	page_length=20,
	searchfield=None,
	reference_doctype=None,
	ignore_user_permissions=False,
):
    search_widget(
        doctype,
        txt.strip(),
        query,
        searchfield=searchfield,
        page_length=page_length,
        filters=filters,
        reference_doctype=reference_doctype,
        ignore_user_permissions=ignore_user_permissions,
    )

    if reference_doctype and reference_doctype == "Sales Order Item":
        temp_list = list(frappe.response["values"])
        for index,item in enumerate(temp_list):
            item = [item[0]]
            item.append("{}{}".format("Last SP: ",frappe.db.get_value("Sales Order Item",{"item_code":item[0]},"rate") or frappe.db.get_value("Item",item[0],"valuation_rate") or 0))
            item.append("{}{}".format("Last PP: ",frappe.db.get_value("Purchase Order Item",{"item_code":item[0]},"rate") or frappe.db.get_value("Item",item[0],"valuation_rate") or "0"))
            temp_list[index] = tuple(item)
        frappe.response["values"] = tuple(temp_list)

    frappe.response["results"] = build_for_autosuggest(frappe.response["values"], doctype=doctype)
    del frappe.response["values"]
