import frappe
from theatre_booking.api import create_booking
def execute():
    try:
        frappe.set_user("Guest")
        # Find the Animal Park show
        shows = frappe.db.sql("""
            SELECT name FROM tabShow WHERE movie = 'Animal Park' AND status = 'Active' LIMIT 1
        """, as_dict=True)
        show_name = shows[0].name if shows else None
        
        if not show_name:
            print("No Animal Park show found")
            return
            
        print("Using show:", show_name)
        res = create_booking(
            show=show_name,
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
        print("Error type:", type(e))
        print("Error message:", str(e))
