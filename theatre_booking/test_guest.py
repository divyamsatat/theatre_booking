import frappe
from theatre_booking.api import create_booking
def execute():
    frappe.set_user("Guest")
    show = frappe.db.get_value("Show", {"status": "Active"})
    try:
        res = create_booking(
            show=show,
            customer_name="Guest Test",
            customer_email="",
            customer_phone="",
            seat_type="Premium",
            num_seats=1
        )
        print("Success:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print("Error:", str(e))
