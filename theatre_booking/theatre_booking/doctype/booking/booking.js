// Copyright (c) 2026, Divyam Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Booking", {

	// ----------------------------------------------------------------
	// On form load — re-apply filters if movie is already set
	// ----------------------------------------------------------------
	refresh(frm) {
		frm.trigger("apply_show_filter");

		// Cancel Booking button for Confirmed bookings
		if (!frm.is_new() && frm.doc.status === "Confirmed") {
			frm.add_custom_button("Cancel Booking", () => {
				frappe.confirm(
					"Are you sure you want to cancel this booking?",
					() => {
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
			}, "Actions").addClass("btn-danger");
		}
	},

	// ----------------------------------------------------------------
	// Step 1: User selects a Movie
	// → Clear any previously selected Show
	// → Filter the Show dropdown to only shows for this movie (status=Active)
	// ----------------------------------------------------------------
	movie(frm) {
		// Clear stale show and its fetched fields whenever movie changes
		frm.set_value("show", "");
		frm.set_value("theatre", "");
		frm.set_value("show_date", "");
		frm.set_value("show_time", "");

		frm.trigger("apply_show_filter");
	},

	// ----------------------------------------------------------------
	// Helper: apply (or clear) the Show filter based on Movie value
	// ----------------------------------------------------------------
	apply_show_filter(frm) {
		const movie = frm.doc.movie;

		if (movie) {
			// Filter shows: must match the selected movie AND be Active
			frm.set_query("show", () => {
				return {
					filters: {
						movie: movie,
						status: "Active"
					}
				};
			});
		} else {
			// No movie selected — allow all active shows
			frm.set_query("show", () => {
				return {
					filters: { status: "Active" }
				};
			});
		}
	},

	// ----------------------------------------------------------------
	// Step 2: User selects a Show
	// → theatre / show_date / show_time auto-fill via fetch_from
	// → Show a helpful summary alert
	// ----------------------------------------------------------------
	show(frm) {
		if (!frm.doc.show) return;

		// fetch_from handles theatre/show_date/show_time automatically.
		// Give a small delay for fetch_from to populate, then show summary.
		setTimeout(() => {
			if (frm.doc.theatre && frm.doc.show_date) {
				frappe.show_alert({
					message: `Show selected: <b>${frm.doc.theatre}</b> on <b>${frappe.datetime.str_to_user(frm.doc.show_date)}</b>`,
					indicator: "blue"
				}, 4);
			}
		}, 800);
	}
});
