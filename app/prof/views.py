# -*- coding: utf-8 -*-
from . import prof

from flask import abort, flash, url_for, render_template, redirect, request, current_app, \
				  jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Subject, Education, Experience, Notification

from ..decorators import prof_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query,\
	room_name, allowed_file, crop_image, crop_first_upload

from werkzeug.utils import secure_filename

from datetime import datetime

import json

import os

from forms import ChangePassword

import time




@prof.before_request
@prof_required
def before_request():
	pass



















@prof.route('/')
def index():
	latest_messages = current_user.contacts_latest_messages()

	return render_template('prof/index.html', user=current_user.serialize(),
	 latest_messages=latest_messages)
















@prof.route('/preferences', methods=['GET', 'POST'])
def settings():
	latest_messages = current_user.contacts_latest_messages()

	password_form = ChangePassword()

	wrong_password = False

	if password_form.validate_on_submit():
		if current_user.verify_password(password_form.old_password.data):
			current_user.change_password(password_form.new_password.data)
			db.session.commit()
			flash("Nouveau mot de passe enregistré")
			return redirect(url_for('auth.logout'))
		else:
			wrong_password = True

	return render_template('prof/settings.html', user=current_user.serialize(),
		password_form = password_form, wrong_password = wrong_password,
		latest_messages=latest_messages)











@prof.route('/reset_unread', methods=['GET', 'POST'])
def reset_unread():
	if request.method == 'POST':
		current_user.unread_msgs = 0
		db.session.commit()

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}



@prof.route('/reset_notification', methods=['GET', 'POST'])
def reset_notification():
	if request.method == 'POST':
		current_user.unread_notifications = 0
		db.session.commit()

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}






@prof.route('/unread_msgs_number')
def unread_msgs():
	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}


@prof.route('/unread_msgs_number_lp', methods=['POST'])
def unread_msgs2():
	"""Long polling"""
	data = request.get_json(silent=True)

	shown_unread = 0

	if data[u'n'] != u'':
		try:
			shown_unread = int(data[u'n'])
		except ValueError:
			time.sleep(15)
			abort(404)

	counter = 0

	while (current_user.unread_msgs == shown_unread) and (counter < 10):
		db.session.commit()
		counter += 1
		#print "sleeping"
		time.sleep(2)

	#print "#########awake"

	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}



@prof.route('/notification_number_lp', methods=['POST'])
def unread_notifications():
	"""Long polling"""
	data = request.get_json(silent=True)

	shown_unread = 0

	if data[u'n'] != u'':
		try:
			shown_unread = int(data[u'n'])
		except ValueError:
			time.sleep(15)
			abort(404)
	counter = 0
	while (current_user.unread_notifications == shown_unread) and (counter < 10):
		db.session.commit()
		print "sleeping {0}".format(counter)
		counter += 1
		time.sleep(2)


	#print "#########awake"

	return json.dumps({'n':current_user.unread_notifications}), 200, {'ContentType':'application/json'}










@prof.route('/fetch_notifications',  methods=['POST'])
def fetch_notifications():
	_ns = Notification.query.filter_by(user = current_user).order_by(Notification.timestamp.desc()).all()
	ns = [n.serialize() for n in _ns]


	return json.dumps(ns), 200, {'ContentType':'application/json'}












@prof.route('/chat/<safe_name>/<int:start>/<int:end>')
def chat_handler(safe_name, start, end):
	"""Handles loading of messages into the chat view"""
	user    = current_user
	contact = User.query.filter_by(safe_name = safe_name).first()

	if not contact or contact.prof:
		abort(404)

	conversation = conversation_query(user, contact).slice(start-1, end).all()

	idd = start
	response = {}

	for message in conversation:
		response[str(idd)] = message.to_dict()
		idd += 1

	return jsonify(response)



















@prof.route('/chat<safe_name>')
def chat(safe_name):
	"""a chat view"""
	latest_messages = current_user.contacts_latest_messages()
	
	client_obj = Client.query.filter(
								Client.user == User.query.filter_by(safe_name=safe_name).first()
								).first()

	if not client_obj:
		abort(404)

	r = room_name(current_user.id, client_obj.user.id)

	return render_template('prof/chat.html', user=current_user.serialize(),
							client=client_obj.serialize(),	latest_messages=latest_messages,
							safe_name=safe_name, room_name=r)













@prof.route('/overview', methods=['GET'])
def profile_overview():
	latest_messages = current_user.contacts_latest_messages()

	prof_obj = current_user.prof

	safe_name = current_user.safe_name


	return render_template('prof/aprof.html', user=current_user.serialize(),
							prof=prof_obj.serialize(),	latest_messages=latest_messages,
							safe_name=safe_name)

















@prof.route('/profile', methods=['GET'])
def profile():
	subjects = Subject.query.all()

	latest_messages = current_user.contacts_latest_messages()
	u = current_user

	placeholders = {
		'title': u.prof.title,
		'birth_date': u.birth_date.strftime("%d/%m/%Y"),
		'about_me': u.prof.about_me,
	}

	educations = current_user.prof.educations
	experiences = current_user.prof.experiences

	"""if request.method == 'POST':
					u.client.about_me = request.form['aboutMe']
					#print request.form['birth_date']
					u.birth_date = datetime.strptime(request.form['birthDate'], "%d/%m/%Y")
					db.session.commit()
					flash(u"enregistré!")"""

	return render_template('prof/profile.html', user=current_user.serialize(),
							prof=current_user.prof, subjects=subjects,
							educations=educations, experiences=experiences,
							latest_messages=latest_messages, placeholders=placeholders)



@prof.route('/profile/general', methods=['POST'])
def profile_general():
	u = current_user
	u.prof.title = request.form['title']
	#print request.form['birth_date']
	u.birth_date = datetime.strptime(request.form['birth_date'], "%d/%m/%Y")
	u.prof.hourly_fee = int(request.form['hourly_fee'])
	u.prof.principal_subject = Subject.query.get(
			int(request.form['principal_subject'])
		)
	u.prof.secondary_subject = Subject.query.get(
			int(request.form['secondary_subject'])
		)
	u.prof.about_me = request.form['about_me']
	db.session.commit()
	flash(u"enregistré!")

	return redirect(url_for('prof.profile'))



@prof.route('/profile/education', methods=['POST'])
def profile_education():
	ed = Education(
		title       = request.form['title'],
		school      = request.form['school'],
		start       = datetime.strptime(request.form['start'], "%m/%Y"),
		end         = datetime.strptime(request.form['end'], "%m/%Y"),
		description = request.form['description'],
		prof        = current_user.prof
		)

	db.session.add(ed)
	db.session.commit()

	flash(u"éducation enregistré!")
	return redirect(url_for('prof.profile'))


@prof.route('/profile/experience', methods=['POST'])
def profile_experience():
	exp = Experience(
		position    = request.form['position'],
		company     = request.form['company'],
		start       = datetime.strptime(request.form['start'], "%m/%Y"),
		end         = datetime.strptime(request.form['end'], "%m/%Y"),
		description = request.form['description'],
		prof        = current_user.prof
		)

	db.session.add(exp)
	db.session.commit()

	flash(u"éxpérience enregistré!")
	return redirect(url_for('prof.profile'))


@prof.route('/profile/education/<int:_id>', methods=['POST'])
def edit_education(_id):
	ed = Education.query.get(_id)
	
	ed.title       = request.form['title'],
	ed.school      = request.form['school'],
	ed.start       = datetime.strptime(request.form['start'], "%m/%Y"),
	ed.end         = datetime.strptime(request.form['end'], "%m/%Y"),
	ed.description = request.form['description'],
	ed.prof        = current_user.prof

	db.session.commit()

	flash(u"éducation enregistré!")
	return redirect(url_for('prof.profile'))


@prof.route('/profile/experience/<int:_id>', methods=['POST'])
def edit_experience(_id):
	exp = Experience.query.get(_id)
	
	exp.position    = request.form['position'],
	exp.company     = request.form['company'],
	exp.start       = datetime.strptime(request.form['start'], "%m/%Y"),
	exp.end         = datetime.strptime(request.form['end'], "%m/%Y"),
	exp.description = request.form['description'],
	exp.prof        = current_user.prof

	db.session.commit()

	flash(u"éxpérience enregistré!")
	return redirect(url_for('prof.profile'))




@prof.route('/profile/delete_education', methods=['POST'])
def delete_education():
	content = request.get_json(silent=True)
	ed = Education.query.get(content[u'_id'])

	db.session.delete(ed)
	db.session.commit()

	return jsonify({'success': True})

@prof.route('/profile/delete_experience', methods=['POST'])
def delete_experience():
	content = request.get_json(silent=True)
	exp = Experience.query.get(content[u'_id'])

	db.session.delete(exp)
	db.session.commit()

	return jsonify({'success': True})


@prof.route('/profile/picture_upload', methods=['GET', 'POST'])
def picture_upload():
	#from flask import session
	#session.pop('_flashes', None)



	latest_messages = current_user.contacts_latest_messages()
	
	if request.method == 'POST':
		if 'profile_picture' not in request.files:
			flash('No profile_picture part')
			return redirect(request.url)

		file = request.files['profile_picture']

		if file.filename== '':
			return redirect(request.url)

		if file and allowed_file(file.filename, set(['png', 'jpg', 'jpeg', 'gif'])):
			ext = os.path.splitext(secure_filename(file.filename))[1]
			filename_original = "original_user_{0}{1}".format(current_user.id, ext)
			file.save(os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename_original))
			
			filename_cropped = "cropped_user_{0}{1}".format(current_user.id, ext)
			crop_first_upload(
				os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename_original),
				os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename_cropped)
				)


			current_user.original_picture = filename_original
			current_user.picture = filename_cropped
			db.session.commit()
			flash(u'image enregistrée')
			return redirect(url_for('prof.profile'))

	return render_template('prof/picture_upload.html', user=current_user.serialize(),
	 prof=current_user.prof, latest_messages=latest_messages)

@prof.route('/profile/picture_upload_handler', methods=['POST'])
def picture_upload_handler():
		if 'profile_picture' not in request.files:
			return jsonify({"msg": "No file selected"}), 400

		file = request.files['profile_picture']

		if file.filename== '':
			return jsonify({"name": "", "size": 0, "error": "File has no name"})

		if file and not allowed_file(file.filename, set(['png', 'jpg', 'jpeg', 'gif'])):
			return jsonify({"name": "", "size": 0, "error": "Choisissez une image avec l'une des extensions suivantes: png, jpg, jpeg, gif"}), 403

		if file and allowed_file(file.filename, set(['png', 'jpg', 'jpeg', 'gif'])):
			ext = os.path.splitext(secure_filename(file.filename))[1]
			
			filename_original = "original_user_{0}{1}".format(current_user.id, ext)
			original_path     = os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename_original)
			
			file.save(original_path)
			
			filename_cropped = "cropped_user_{0}{1}".format(current_user.id, ext)
			cropped_path     = 	os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename_cropped)

			crop_first_upload(original_path, cropped_path)

			original_size = os.path.getsize(original_path)

			current_user.original_picture = filename_original
			current_user.picture = filename_cropped
			db.session.commit()
			flash(u'image enregistrée')

			resp_dict = {
				"files": [
					{
						"name"         : filename_original,
						"size"         : original_size,
						"url"          : url_for('main.profile_picture', filename=filename_original, _external=True),
						"thumbnailUrl" : url_for('main.profile_picture', filename=filename_original, _external=True)
					}
				]}
			
			return jsonify(resp_dict)


@prof.route('/profile/picture_crop', methods=['POST'])
def picture_crop():
	crop_data = request.get_json(silent=True)

	src  = os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], current_user.original_picture)
	dest  = os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], current_user.picture)

	crop_image(src, dest, int(crop_data['x']), int(crop_data['y']),
			   int(crop_data['width']), int(crop_data['height']))

	return jsonify({'success': True})
