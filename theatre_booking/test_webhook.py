import frappe
import json
import hmac
import hashlib
import requests

def execute():
    # 1. Set the webhook secret in settings
    settings = frappe.get_doc("Theatre Booking Settings")
    settings.razorpay_webhook_secret = "test_webhook_secret_123"
    settings.save()
    frappe.db.commit()
    print("Set webhook secret to 'test_webhook_secret_123'")

    # 2. Create a dummy Booking with a fake razorpay_order_id
    # Get a random Active show
    show = frappe.db.get_value("Show", {"status": "Active"})
    if not show:
        print("No active shows to test with.")
        return

    booking = frappe.get_doc({
        "doctype": "Booking",
        "show": show,
        "customer_name": "Webhook Tester",
        "seat_type": "Regular",
        "num_seats": 1,
        "razorpay_order_id": "order_test_webhook_123",
        "status": "Pending Payment"
    })
    booking.insert(ignore_permissions=True)
    frappe.db.commit()
    print(f"Created pending booking {booking.name} with razorpay_order_id=order_test_webhook_123")

    # 3. Craft webhook payload
    payload = {
      "entity": "event",
      "event": "payment.captured",
      "payload": {
        "payment": {
          "entity": {
            "order_id": "order_test_webhook_123",
            "status": "captured"
          }
        }
      }
    }
    
    raw_body = json.dumps(payload, separators=(',', ':'))
    
    # 4. Generate Signature
    secret = "test_webhook_secret_123"
    signature = hmac.new(
        secret.encode('utf-8'),
        raw_body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    print(f"Generated Signature: {signature}")

    # 5. Send HTTP request to local endpoint
    url = frappe.utils.get_url("/api/method/theatre_booking.api.razorpay_webhook")
    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature
    }
    
    print(f"Sending POST to {url}")
    response = requests.post(url, data=raw_body, headers=headers)
    
    print(f"Response Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    # 6. Verify if booking status changed to Confirmed
    frappe.db.rollback() # to avoid stale read if any
    updated_status = frappe.db.get_value("Booking", booking.name, "status")
    print(f"Booking {booking.name} status is now: {updated_status}")
    
    if updated_status == "Confirmed":
        print("SUCCESS! Webhook verified and updated the booking.")
    else:
        print("FAILED! Webhook did not update the booking.")
