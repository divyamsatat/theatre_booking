// Copyright (c) 2026, Divyam Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Show", {
	// ----------------------------------------------------------------
	// Helper: apply (or clear) the Screen filter based on Theatre value
	// ----------------------------------------------------------------
	apply_screen_filter(frm) {
		const theatre = frm.doc.theatre;

		if (theatre) {
			// Theatre is set → restrict Screen to only screens of that Theatre
			frm.set_query("screen", () => {
				return {
					filters: {
						theatre: theatre
					}
				};
			});
		} else {
			// Theatre is empty → remove any restriction on Screen
			frm.set_query("screen", () => {
				return {};
			});
		}
	},

	// ----------------------------------------------------------------
	// Situation 1 & new-doc load:
	// Fires whenever the form is loaded/refreshed (existing OR new record)
	// ----------------------------------------------------------------
	refresh(frm) {
		frm.trigger("apply_screen_filter");

		if (!frm.is_new()) {
			frappe.show_alert("Show loaded successfully");

			// ----------------------------------------------------------------
			// Cancel Show button (only visible when show is Active)
			// ----------------------------------------------------------------
			if (frm.doc.status === "Active") {
				frm.add_custom_button("Cancel Show", () => {
					frappe.confirm(
						"Are you sure you want to cancel this show? All confirmed bookings will also be cancelled.",
						() => {
							// YES clicked — call server API
							frappe.call({
								method: "theatre_booking.api.cancel_show",
								args: { show_name: frm.doc.name },
								freeze: true,
								freeze_message: "Cancelling show and bookings...",
								callback(r) {
									if (r.message) {
										const count = r.message.cancelled_bookings;
										frappe.show_alert({
											message: `Show cancelled. ${count} booking(s) also cancelled.`,
											indicator: "red"
										}, 5);
										frm.reload_doc();
									}
								}
							});
						},
						() => {
							// NO clicked
							frappe.show_alert({
								message: "Cancelled. Show is still active.",
								indicator: "green"
							}, 3);
						}
					);
				});
			}

			// ----------------------------------------------------------------
			// Add Notes button → frappe.prompt (Concept 4)
			// ----------------------------------------------------------------
			frm.add_custom_button("Add Notes", () => {
				frappe.prompt(
					{ fieldname: "notes", label: "Notes", fieldtype: "Small Text", reqd: 1 },
					(values) => {
						frappe.show_alert({
							message: `Note saved: ${values.notes}`,
							indicator: "green"
						}, 3);
					},
					"Add Notes",
					"Save Note"
				);
			});

			// ----------------------------------------------------------------
			// Book Seats button → frappe.ui.Dialog → frappe.call to api.py
			// (only available when Show is Active)
			// ----------------------------------------------------------------
			if (frm.doc.status === "Active") {
				frm.add_custom_button("Book Seats", () => {
					const d = new frappe.ui.Dialog({
						title: "Book Seats",
						fields: [
							{ label: "Customer Name", fieldname: "customer_name", fieldtype: "Data", reqd: 1 },
							{ label: "Customer Email", fieldname: "customer_email", fieldtype: "Data" },
							{ label: "Customer Phone", fieldname: "customer_phone", fieldtype: "Data" },
							{ label: "Seat Type", fieldname: "seat_type", fieldtype: "Select", options: "Regular\nPremium", reqd: 1 },
							{ label: "Number of Seats", fieldname: "num_seats", fieldtype: "Int", reqd: 1 },
						],
						primary_action_label: "Confirm Booking",
						primary_action(values) {
							d.hide();

							frappe.call({
								method: "theatre_booking.api.create_booking",
								args: {
									show: frm.doc.name,
									customer_name: values.customer_name,
									customer_email: values.customer_email || "",
									customer_phone: values.customer_phone || "",
									seat_type: values.seat_type,
									num_seats: values.num_seats,
								},
								freeze: true,
								freeze_message: "Creating booking...",
								callback(r) {
									if (r.message) {
										frappe.show_alert({
											message: `Booking ${r.message} confirmed for ${values.customer_name}!`,
											indicator: "green"
										}, 5);
									}
								}
							});
						}
					});
					d.show();
				});
			}
		}
	},

	// ----------------------------------------------------------------
	// Situation 2 & 3:
	// Fires whenever the Theatre field value changes
	// ----------------------------------------------------------------
	theatre(frm) {
		// Situation 3 – Theatre changed after Screen was already chosen:
		// clear the stale Screen value so the user must re-pick a valid one
		if (frm.doc.screen) {
			frappe.model.set_value(frm.doctype, frm.docname, "screen", "");
		}

		// Re-apply the filter with the new (or empty) Theatre value
		frm.trigger("apply_screen_filter");
	}
});

