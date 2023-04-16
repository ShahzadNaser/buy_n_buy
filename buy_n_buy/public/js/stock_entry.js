frappe.ui.form.handlers["Stock Entry Detail"]["item_code"] = [];
frappe.ui.form.on('Stock Entry', {
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

			if (item.s_warehouse) filters["warehouse"] = item.s_warehouse;

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
frappe.ui.form.on('Stock Entry Detail', {
	item_code: function(frm,cdt, cdn) {
        var d = locals[cdt][cdn];
        if(d.item_code) {
            var args = {
                'item_code'			: d.item_code,
                'warehouse'			: cstr(d.s_warehouse) || cstr(d.t_warehouse),
                'transfer_qty'		: d.transfer_qty,
                'serial_no'		: d.serial_no,
                'batch_no'      : d.batch_no,
                'bom_no'		: d.bom_no,
                'expense_account'	: d.expense_account,
                'cost_center'		: d.cost_center,
                'company'		: frm.doc.company,
                'qty'			: d.qty,
                'voucher_type'		: frm.doc.doctype,
                'voucher_no'		: d.name,
                'allow_zero_valuation': 1,
            };

            return frappe.call({
                doc: frm.doc,
                method: "get_item_details",
                args: args,
                callback: function(r) {
                    if(r.message) {
                        var d = locals[cdt][cdn];
                        $.each(r.message, function(k, v) {
                            if (v) {
                                frappe.model.set_value(cdt, cdn, k, v); // qty and it's subsequent fields weren't triggered
                            }
                        });
                        refresh_field("items");

                        let no_batch_serial_number_value = !d.serial_no;
                        if (d.has_batch_no && !d.has_serial_no) {
                            // check only batch_no for batched item
                            no_batch_serial_number_value = !d.batch_no;
                        }
                        console.log("=============in======================");
                        if (no_batch_serial_number_value && !frappe.flags.hide_serial_batch_dialog) {
                            // erpnext.stock.select_batch_and_serial_no(frm, d);
                        }
                        frm.events.update_item_details(d);
                    }
                }
            });
        }
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