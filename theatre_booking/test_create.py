import frappe
from theatre_booking.api import create_booking
def execute():
    show = frappe.db.get_value("Show", {"status": "Active"})
    try:
        res = create_booking(
            show=show,
            customer_name="Divyam Jain",
            customer_email="jaindivyam200@gmail.com",
            customer_phone="+919999999999",
            seat_type="Premium",
            num_seats=5
        )
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error:", str(e))
