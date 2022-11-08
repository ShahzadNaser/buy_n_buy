$(window).on('load', doctype_loaded);
function doctype_loaded(event) {
    console.log("====doctype_loaded========");

    frappe.after_ajax(function () {
        console.log("====HERE==========");
    });
}