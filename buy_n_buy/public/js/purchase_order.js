frappe.ui.form.on('Purchase Order Item', {
	item_code: function(frm,cdt, cdn) {
        console.log(cdt, cdn);
		var item = frappe.get_doc(cdt, cdn);
        return frm.call({
            method: "buy_n_buy.events.events.get_item_details",
            child: item,
            args: {
                "item_code": item.item_code
            },
            callback: function(r) {
                if(r.message){
                    frappe.model.set_value(item.doctype, item.name,"cbm_1", flt(r.message.cbm_1));
                    frappe.model.set_value(item.doctype, item.name,"cbm_2", flt(r.message.cbm_2));
                    frappe.model.set_value(item.doctype, item.name,"cbm_3", flt(r.message.cbm_3));
                    var boxes = flt(1/r.message.fac);
                    frappe.model.set_value(item.doctype, item.name,"con_fact",flt(r.message.fac));
                    frappe.model.set_value(item.doctype, item.name,"boxes",boxes);
                    if((r.message.cbm_1 || 0) * (r.message.cbm_2 || 0) * (r.message.cbm_3 || 0) > 0){
                        var per_ctn_cbm = flt((r.message.cbm_1 || 0) * (r.message.cbm_2 || 0) * (r.message.cbm_3 || 0)/1000000 );
                        frappe.model.set_value(item.doctype, item.name,"per_ctn_cbm", per_ctn_cbm);
                        frappe.model.set_value(item.doctype, item.name,"total_cbm", flt(per_ctn_cbm * boxes));    
                    }
                }
            }
        });
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
    }
});