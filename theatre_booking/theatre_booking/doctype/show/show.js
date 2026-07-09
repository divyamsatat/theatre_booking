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

			frm.add_custom_button("Cancel Show", () => {
				frappe.confirm(
					"Are you sure you want to cancel this show?",
					() => {
						// YES clicked
						frappe.show_alert({
							message: "Show has been cancelled!",
							indicator: "red"
						}, 3);
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
