import frappe
def execute():
    errors = frappe.db.get_all('Error Log', ['error'], order_by='creation desc', limit=10)
    for e in errors:
        if 'theatre_booking' in e.error:
            print('=== ERROR ===')
            print(e.error)
            return
