from . import __version__ as app_version

app_name = "buy_n_buy"
app_title = "Buy N Buy"
app_publisher = "Shahzad Naser"
app_description = "buy_n_buy"
app_email = "shahzadnaser1122@gmail.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/buy_n_buy/css/buy_n_buy.css"
# app_include_js = "/assets/buy_n_buy/js/buy_n_buy.js"

# include js, css files in header of web template
# web_include_css = "/assets/buy_n_buy/css/buy_n_buy.css"
# web_include_js = "/assets/buy_n_buy/js/buy_n_buy.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "buy_n_buy/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Sales Order" : "public/js/sales_order.js",
    "Purchase Order" : "public/js/purchase_order.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "buy_n_buy.utils.jinja_methods",
#	"filters": "buy_n_buy.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "buy_n_buy.install.before_install"
# after_install = "buy_n_buy.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "buy_n_buy.uninstall.before_uninstall"
# after_uninstall = "buy_n_buy.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "buy_n_buy.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
#	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
	"Purchase Order": {
		"on_submit": "buy_n_buy.events.events.make_new_batch",
	}
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"buy_n_buy.tasks.all"
#	],
#	"daily": [
#		"buy_n_buy.tasks.daily"
#	],
#	"hourly": [
#		"buy_n_buy.tasks.hourly"
#	],
#	"weekly": [
#		"buy_n_buy.tasks.weekly"
#	],
#	"monthly": [
#		"buy_n_buy.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "buy_n_buy.install.before_tests"

# Overriding Methods
# ------------------------------
#
override_whitelisted_methods = {
	"erpnext.selling.doctype.sales_order.sales_order.make_delivery_note": "buy_n_buy.events.sales_order.make_delivery_note",
	"erpnext.buying.doctype.purchase_order.purchase_order.make_purchase_receipt": "buy_n_buy.events.purchase_order.make_purchase_receipt"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "buy_n_buy.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"buy_n_buy.auth.validate"
# ]
