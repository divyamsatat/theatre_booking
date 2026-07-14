// Copyright (c) 2026, Divyam Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Booking", {
	refresh(frm) {
		// Show "Cancel Booking" button only for Confirmed bookings that are saved
		if (!frm.is_new() && frm.doc.status === "Confirmed") {
			frm.add_custom_button("Cancel Booking", () => {
				frappe.confirm(
					"Are you sure you want to cancel this booking?",
					() => {
						// YES — set status to Cancelled and save
						frm.set_value("status", "Cancelled");
						frm.save().then(() => {
							frappe.show_alert({
								message: "Booking has been cancelled.",
								indicator: "red"
							}, 4);
						});
					},
					() => {
						frappe.show_alert({
							message: "Booking remains active.",
							indicator: "green"
						}, 3);
					}
				);
			}, /* group */ "Actions").addClass("btn-danger");
		}
	}
});
