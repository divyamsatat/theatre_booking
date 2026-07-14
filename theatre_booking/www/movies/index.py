import frappe

no_cache = 1


def get_context(context):
	context.no_breadcrumbs = True
	context.no_header = True
	context.no_footer = True
	context.title = "CinéBook — Now Showing"
	# Movies will be loaded client-side via the get_movies API
	# to avoid Frappe guest-context SQL permission issues
	context.movies = []
