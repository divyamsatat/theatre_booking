import frappe
def execute():
    errors = frappe.db.get_all('Error Log', ['error', 'method'], order_by='creation desc', limit=5)
    for e in errors:
        print("=== ERROR ===")
        print("Method:", e.method)
        print(e.error)
