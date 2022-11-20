frappe.ui.form.on('Sales Order', {
    refresh(frm){

        frm.set_query("batch_no", "items", function(doc, cdt, cdn) {
		// Show item's batches in the dropdown of batch no
		var item = frappe.get_doc(cdt, cdn);

		if(!item.item_code) {
			frappe.throw(__("Please enter Item Code to get batch no"));
		} else if (doc.doctype == "Purchase Receipt" ||
			(doc.doctype == "Purchase Invoice" && doc.update_stock)) {
			return {
				filters: {'item': item.item_code}
			}
		} else {
			let filters = {
				'item_code': item.item_code,
				'posting_date': frm.doc.posting_date || frappe.datetime.nowdate(),
			}

			if (doc.is_return) {
				filters["is_return"] = 1;
			}

			if (item.warehouse) filters["warehouse"] = item.warehouse;

			return {
				query : "erpnext.controllers.queries.get_batch_no",
				filters: filters
			}
		}
          });
    },
    update_item_details: function(item){
        console.log(item);
        return cur_frm.call({
            method: "buy_n_buy.events.events.get_item_details",
            child: item,
            args: {
                "item_code": item.item_code,
                "warehouse": item.warehouse || cur_frm.doc.set_warehouse || ""

            },
            callback: function(r) {
                if(r.message){
                    frappe.model.set_value(item.doctype, item.name,"cbm_1", flt(r.message.cbm_1));
                    frappe.model.set_value(item.doctype, item.name,"cbm_2", flt(r.message.cbm_2));
                    frappe.model.set_value(item.doctype, item.name,"cbm_3", flt(r.message.cbm_3));
                    var boxes = flt((item.qty || 1)/r.message.fac);
                    frappe.model.set_value(item.doctype, item.name,"con_fact",flt(r.message.fac));
                    frappe.model.set_value(item.doctype, item.name,"boxes",boxes);
                    frappe.model.set_value(item.doctype, item.name,"stock_qty1",r.message.actual_qty);
                    if((r.message.cbm_1 || 0) * (r.message.cbm_2 || 0) * (r.message.cbm_3 || 0) > 0){
                        var per_ctn_cbm = flt((r.message.cbm_1 || 0) * (r.message.cbm_2 || 0) * (r.message.cbm_3 || 0)/1000000 );
                        frappe.model.set_value(item.doctype, item.name,"per_ctn_cbm", per_ctn_cbm);
                        frappe.model.set_value(item.doctype, item.name,"total_cbm", flt(per_ctn_cbm * boxes));    
                    }
                }
            }
        });

    }
});
frappe.ui.form.on('Sales Order Item', {
	item_code: function(frm,cdt, cdn) {
		var item = frappe.get_doc(cdt, cdn);
        frm.events.update_item_details(item)
    },
    qty: function(frm, cdt, cdn){
		var item = frappe.get_doc(cdt, cdn);
        var per_ctn_cbm = flt((item.cbm_1 || 0) * (item.cbm_2 || 0) * (item.cbm_3 || 0)/1000000 )
        var boxes = flt(item.qty/item.con_fact);
        frappe.model.set_value(item.doctype, item.name,"boxes",boxes);
        frappe.model.set_value(item.doctype, item.name,"per_ctn_cbm", per_ctn_cbm);
        frappe.model.set_value(item.doctype, item.name,"total_cbm", flt(per_ctn_cbm * boxes)); 
    },
    boxes: function(frm, cdt, cdn){
		var item = frappe.get_doc(cdt, cdn);
        var per_ctn_cbm = flt((item.cbm_1 || 0) * (item.cbm_2 || 0) * (item.cbm_3 || 0)/1000000 )
        var qty = flt(item.boxes*item.con_fact);

        frappe.model.set_value(item.doctype, item.name,"per_ctn_cbm", per_ctn_cbm);
        frappe.model.set_value(item.doctype, item.name,"total_cbm", flt(per_ctn_cbm * item.boxes));

        frappe.model.set_value(item.doctype, item.name,"qty",qty);
    },
    warehouse: function(frm, cdt,cdn){
		var item = frappe.get_doc(cdt, cdn);
        frm.events.update_item_details(item)
    },
    delivery_warehouse: function(frm, cdt,cdn){
		var item = frappe.get_doc(cdt, cdn);
        frappe.model.set_value(cdt, cdn,"warehouse",item.delivery_warehouse);
    }
});