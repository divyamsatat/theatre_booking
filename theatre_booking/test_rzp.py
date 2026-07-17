import frappe
def execute():
    settings_name = frappe.db.get_value("Theater Booking Settings", filters={}, fieldname="name")
    settings = frappe.get_doc("Theater Booking Settings", settings_name)
    import razorpay
    client = razorpay.Client(auth=(settings.razorpay_key_id, settings.get_password("razorpay_key_secret")))
    
    try:
        order = client.order.create({
            "amount": 250000,
            "currency": "INR",
            "receipt": "test_receipt"
        })
        print("Success:", order)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error:", str(e))
