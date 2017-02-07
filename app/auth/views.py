from . import auth

from flask import current_app, url_for

@auth.route('/login')
def login():
	return "Login view"

