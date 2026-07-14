// Copyright (c) 2026, Divyam Jain and contributors
// For license information, please see license.txt

frappe.ui.form.on("Screen", {
	refresh(frm) {
		// ----------------------------------------------------------------
		// "Generate Seats" button — reads row_config and populates seats
		// ----------------------------------------------------------------
		frm.add_custom_button("Generate Seats", () => {
			if (!frm.doc.row_config || frm.doc.row_config.length === 0) {
				frappe.msgprint({
					title: "No Row Configuration",
					message: "Please add at least one row in the <b>Row Configuration</b> table before generating seats.",
					indicator: "orange"
				});
				return;
			}

			// Confirm before wiping existing seats
			const confirmMsg = frm.doc.seats && frm.doc.seats.length > 0
				? "This will <b>replace all existing seats</b> with a fresh set based on the row configuration. Continue?"
				: "Generate seats based on the row configuration?";

			frappe.confirm(confirmMsg, () => {
				// Clear existing seats
				frm.doc.seats = [];
				frm.refresh_field("seats");

				let totalGenerated = 0;

				// For each row config entry, generate num_seats individual seat rows
				frm.doc.row_config.forEach(row => {
					if (!row.row_label || !row.num_seats || row.num_seats < 1) return;

					for (let i = 1; i <= row.num_seats; i++) {
						const child = frappe.model.add_child(frm.doc, "Seat", "seats");
						child.row = row.row_label;
						child.seat_number = String(i);
						child.seat_type = row.seat_type || "Regular";
						totalGenerated++;
					}
				});

				// Update total_seats field
				frappe.model.set_value(frm.doctype, frm.docname, "total_seats", totalGenerated);

				frm.refresh_field("seats");
				frm.refresh_field("total_seats");

				frappe.show_alert({
					message: `✅ Generated ${totalGenerated} seats across ${frm.doc.row_config.length} row(s). Don't forget to Save!`,
					indicator: "green"
				}, 5);
			});
		}, /* group */ "⚙ Actions");

		// Update total_seats indicator on refresh
		if (frm.doc.seats && frm.doc.seats.length > 0) {
			frm.set_value("total_seats", frm.doc.seats.length);
		}
	},

	// Live-update the total_seats counter when row_config changes
	row_config_add(frm) {
		frm.trigger("recalculate_total");
	},
	row_config_remove(frm) {
		frm.trigger("recalculate_total");
	},

	recalculate_total(frm) {
		let total = 0;
		(frm.doc.row_config || []).forEach(r => {
			total += (r.num_seats || 0);
		});
		frm.set_value("total_seats", total);
	}
});

// Live-update total when num_seats changes in a row
frappe.ui.form.on("Screen Row Config", {
	num_seats(frm) {
		frm.trigger("recalculate_total");
	}
});
