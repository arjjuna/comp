from . import main
import os

from flask import abort, flash, url_for, render_template, redirect, request, current_app
from flask_login import current_user


@main.route('/')
def index():
	if current_user.is_anonymous():
		return render_template('main/index.html')
	elif current_user.is_client():
		return redirect(url_for('client.index'))
	elif current_user.is_prof():
		return redirect(url_for('prof.index'))

@main.route('/profile_picture/<filename>')
def profile_picture(filename):
	return redirect(url_for('static', filename=os.path.join(current_app.config['USERS_UPLOAD_FOLDER_RELATIVE'], filename)))