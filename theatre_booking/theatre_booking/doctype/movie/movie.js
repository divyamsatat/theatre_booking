// Copyright (c) 2026, Divyam Jain and contributors
// For license information, please see license.txt


frappe.ui.form.on("Movie", {
    refresh(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button("Movie Info", () => {
                frappe.msgprint({
                    title: "Movie Details",
                    indicator: "blue",
                    message: `
                        <b>Movie:</b> ${frm.doc.movie_name}<br>
                        <b>Genre:</b> ${frm.doc.genre}<br>
                        <b>Language:</b> ${frm.doc.language}
                    `
                });
            });
        }
    },
});

