import razorpay
def execute():
    client = razorpay.Client(auth=("rzp_test_TEWSPyYgFp6uSm", "************************"))
    try:
        order = client.order.create({"amount": 1000, "currency": "INR"})
    except Exception as e:
        print("Error type:", type(e).__name__)
        print("Error message:", str(e))
