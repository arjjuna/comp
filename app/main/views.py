from . import main

from flask import current_app, url_for


@main.route('/')
def index():
	return "Index Page"