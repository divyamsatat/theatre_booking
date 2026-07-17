import frappe
def execute():
    settings_name = frappe.db.get_value("Theater Booking Settings", filters={}, fieldname="name")
    if not settings_name:
        print("No Theater Booking Settings found")
        return
        
    doc = frappe.get_doc("Theater Booking Settings", settings_name)
    doc.razorpay_key_id = "rzp_test_TEWSPyYgFp6uSm"
    doc.razorpay_key_secret = "xuy4np0puiRTcJaXZK2IoIjh"
    doc.save()
    frappe.db.commit()
    print("Successfully updated Razorpay keys")
