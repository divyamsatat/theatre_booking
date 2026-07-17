import frappe

def execute():
    doc = frappe.get_doc("DocType", "Theatre Booking Settings")
    
    # Check if field already exists to prevent duplicates
    exists = False
    for f in doc.fields:
        if f.fieldname == "razorpay_webhook_secret":
            exists = True
            break
            
    if not exists:
        doc.append("fields", {
            "fieldname": "razorpay_webhook_secret",
            "fieldtype": "Password",
            "label": "Razorpay Webhook Secret",
            "in_list_view": 1
        })
        doc.save()
        frappe.db.commit()
        print("Successfully added razorpay_webhook_secret field")
    else:
        print("Field razorpay_webhook_secret already exists")
