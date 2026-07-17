import frappe
def execute():
    for e in frappe.db.get_all("Error Log", fields=["method", "error"], order_by="creation desc", limit=10):
        if "BadRequestError" not in e.error and "Not enough Regular seats" not in e.error:
            print("==========")
            print(e.error)
            break
