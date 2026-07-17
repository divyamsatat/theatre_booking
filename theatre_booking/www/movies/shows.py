import frappe

no_cache = 1

def get_context(context):
    context.no_cache = 1
    if hasattr(frappe.local, "session") and hasattr(frappe.local.session, "data"):
        context.csrf_token = frappe.local.session.data.csrf_token
    else:
        context.csrf_token = ""
