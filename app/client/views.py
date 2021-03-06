# -*- coding: utf-8 -*-
import os

from . import client

from flask import abort, flash, url_for, render_template,\
				  redirect, request, current_app, jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Subject, Notification, Level, City

from ..decorators import client_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query, room_name, \
			search_profs, allowed_file, crop_image, crop_first_upload

from unidecode import unidecode

import dateutil.parser

from datetime import datetime

from forms import ProfileForm, ChangePassword

from werkzeug.utils import secure_filename

import json

import time










@client.before_request
@client_required
def before_request():
	pass









@client.route('/')
def index():
	"""Index of the client side"""
	latest_messages = current_user.contacts_latest_messages()
	
	return render_template('client/index.html', user=current_user.serialize(),
	 latest_messages=latest_messages)





@client.route('/reset_unread', methods=['GET', 'POST'])
def reset_unread():
	if request.method == 'POST':
		current_user.unread_msgs = 0
		db.session.commit()

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}




@client.route('/reset_notification', methods=['GET', 'POST'])
def reset_notification():
	if request.method == 'POST':
		current_user.unread_notifications = 0
		db.session.commit()

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}













@client.route('/unread_msgs_number')
def unread_msgs():
	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}





@client.route('/unread_msgs_number_lp', methods=['POST'])
def unread_msgs2():
	"""Long polling"""
	data = request.get_json(silent=True)

	shown_unread = 0

	if data[u'n'] != u'':
		try:
			shown_unread = int(data[u'n'])
		except ValueError:
			time.sleep(10*current_app.config['LONG_POLL_SLEEP'])
			abort(404)
	
	counter = 0
	while (current_user.unread_msgs == shown_unread) and (counter < 10):
		db.session.commit()
		counter += 1 
		#print "sleeping"
		time.sleep(current_app.config['LONG_POLL_SLEEP'])

	#print "#########awake"

	db.session.close()

	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}


@client.route('/notification_number_lp', methods=['POST'])
def unread_notifications():
	"""Long polling"""
	data = request.get_json(silent=True)

	shown_unread = 0

	if data[u'n'] != u'':
		try:
			shown_unread = int(data[u'n'])
		except ValueError:
			time.sleep(10*current_app.config['LONG_POLL_SLEEP'])
			abort(404)
	counter = 0
	while (current_user.unread_notifications == shown_unread) and (counter < 10):
		db.session.commit()
		#print "sleeping {0}".format(counter)
		counter += 1
		time.sleep(current_app.config['LONG_POLL_SLEEP'])


	#print "#########awake"

	return json.dumps({'n':current_user.unread_notifications}), 200, {'ContentType':'application/json'}

















@client.route('/fetch_notifications',  methods=['POST'])
def fetch_notifications():
	_ns = Notification.query.filter_by(user = current_user).order_by(Notification.timestamp.desc()).all()
	ns = [n.serialize() for n in _ns]


	return json.dumps(ns), 200, {'ContentType':'application/json'}


@client.route('/fetch_notifications_html',  methods=['POST'])
def fetch_notifications_html():
	_ns = Notification.query.filter_by(user = current_user).order_by(Notification.timestamp.desc()).all()
	ns = [n.serialize() for n in _ns][:6]


	return render_template('client/_latest_notifications.html', latest_notifications=ns)




@client.route('/fetch_messages_html',  methods=['POST'])
def fetch_messages_html():
	latest_messages = current_user.contacts_latest_messages()

	for m in latest_messages:
		m.pop('iso_date', None)
		m['message_obj'] = m['message_obj'].serialize()
		m['who'] = m['who'].serialize()

	#print m

	return render_template('client/_latest_messages.html', latest_messages=latest_messages[:6])






@client.route('/fetch_messages',  methods=['POST'])
def fetch_messages():
	latest_messages = current_user.contacts_latest_messages()

	for m in latest_messages:
		m.pop('iso_date', None)
		m['message_obj'] = m['message_obj'].serialize()
		m['who'] = m['who'].serialize()

	#print m

	return json.dumps(latest_messages), 200, {'ContentType':'application/json'}




















@client.route('/recherche_o')
def search_o():
	"""Where a client looks for profs"""
	latest_messages = current_user.contacts_latest_messages()
	
	keywords = request.args.get('keywords')


	prof_list = Prof.query.all()

	return render_template('client/search.html', user=current_user.serialize(),
							latest_messages=latest_messages, keywords=keywords,
							prof_list=prof_list)



@client.route('/recherche', methods=['GET'])
def search():
	"""Where a client looks for profs"""
	latest_messages = current_user.contacts_latest_messages()

	keywords = None
	subject  = None

	_subject = request.args.get('subject')
	_keywords = request.args.get('keywords')

	if _subject:
		all_subjects = Subject.query.all()

		for s in all_subjects:
			if s.url_safe_name() == _subject:
				subject = s
				break
	elif _keywords:
		keywords = _keywords


	form_choices = {
		'subjects': Subject.query.all(),
		'levels'  : Level.query.all(),
		'cities'  : City.query.all()
	}
	
	
	return render_template('client/search.html', user=current_user.serialize(),
							latest_messages=latest_messages, keywords=keywords,
							form_choices=form_choices, default_subject=subject,
							 default_keywords=keywords)





@client.route('/recherche/aprof', methods=['POST'])
def _search_aprof():
	"""Fetches the html for a prof in the search results"""

	query_dict = request.get_json(silent=True)

	"""{
			u'age_range': {u'to': 80, u'from': 18},
			u'levels': [], u'subjects': [], u'keywords': u'',
			u'price_range': {u'to': 400, u'from': 50}, u'cities': []
		}"""
	prof_list = search_profs(query_dict)


	return render_template('client/_search_prof.html', prof_list=prof_list)







@client.route('/recherche/subject', methods=['POST'])
def _search_subject():
	"""Fetches the html for a prof in the search results"""

	query_dict = request.get_json(silent=True)

	"""{
			u'age_range': {u'to': 80, u'from': 18},
			u'levels': [], u'subjects': [], u'keywords': u'',
			u'price_range': {u'to': 400, u'from': 50}, u'cities': []
		}"""

	subject = Subject.query.get(int(query_dict[u'subject_id']))

	if subject:
		prof_list = Prof.query.filter(or_(
			Prof.principal_subject == subject,
			Prof.secondary_subject == subject
			))
	else:
		prof_list = []


	return render_template('client/_search_prof.html', prof_list=prof_list)




























@client.route('/prof/<safe_name>')
def aprof(safe_name):
	"""How a client views a prof"""
	latest_messages = current_user.contacts_latest_messages()
	prof_obj = Prof.query.filter(
								Prof.user == User.query.filter_by(safe_name=safe_name).first()
								).first()
	
	if not prof_obj:
		abort(404)

	return render_template('client/aprof.html', user=current_user.serialize(),
							prof=prof_obj.serialize(),	latest_messages=latest_messages,
							safe_name=safe_name)















































@client.route('/chat/<safe_name>/<int:start>/<int:end>')
def chat_handler(safe_name, start, end):
	"""Handels loading of messages into the chat view"""
	user    = current_user
	contact = User.query.filter_by(safe_name = safe_name).first()

	if not contact:
		abort(404)

	conversation = conversation_query(user, contact).slice(start-1, end).all()
	if not conversation[0].seen:
		#print "seeeing"
		conversation[0].seen = True
		db.session.add(conversation[0])
		db.session.commit()

	idd = start
	response = {}

	for m in conversation:
		response[str(idd)] = m.to_dict()
		idd += 1

	return jsonify(response)














@client.route('/chat<safe_name>')
def chat(safe_name):
	"""a chat view"""
	latest_messages = current_user.contacts_latest_messages()
	latest_messages = current_user.contacts_latest_messages()
	
	prof_obj = Prof.query.filter(
								Prof.user == User.query.filter_by(safe_name=safe_name).first()
								).first()

	if not prof_obj:
		abort(404)

	r = room_name(current_user.id, prof_obj.user.id)

	return render_template('client/chat.html', user=current_user.serialize(),
							prof=prof_obj.serialize(),	latest_messages=latest_messages,
							safe_name=safe_name, room_name=r)


































@client.route('/profile', methods=['GET', 'POST'])
def profile():
	latest_messages = current_user.contacts_latest_messages()
	u = current_user

	placeholders = {
		'about_me': u.client.about_me,
		'birth_date': u.birth_date.strftime("%d/%m/%Y"),
	}

	"""if request.method == 'POST':
					u.client.about_me = request.form['aboutMe']
					#print request.form['birth_date']
					u.birth_date = datetime.strptime(request.form['birthDate'], "%d/%m/%Y")
					db.session.commit()
					flash(u"enregistré!")"""

	return render_template('client/profile.html', user=current_user.serialize(),
							latest_messages=latest_messages, placeholders=placeholders)



@client.route('/profile/general', methods=['POST'])
def profile_general():
	u = current_user
	u.client.about_me = request.form['about_me']
	#print request.form['birth_date']
	u.birth_date = datetime.strptime(request.form['birth_date'], "%d/%m/%Y")
	db.session.commit()
	flash(u"enregistré!")

	return redirect(url_for('client.profile'))



@client.route('/profile/picture_upload', methods=['GET'])
def picture_upload():

	latest_messages = current_user.contacts_latest_messages()

	return render_template('client/picture_upload.html', user=current_user.serialize(),
	 						latest_messages=latest_messages)



@client.route('/profile/picture_upload_handler', methods=['POST'])
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






@client.route('/profile/picture_crop', methods=['POST'])
def picture_crop():
	crop_data = request.get_json(silent=True)

	src  = os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], current_user.original_picture)
	dest  = os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], current_user.picture)

	crop_image(src, dest, int(crop_data['x']), int(crop_data['y']),
			   int(crop_data['width']), int(crop_data['height']))

	return jsonify({'success': True})













@client.route('/preferences', methods=['GET', 'POST'])
def settings():
	latest_messages = current_user.contacts_latest_messages()

	password_form = ChangePassword()

	wrong_password = False

	if password_form.validate_on_submit():
		if current_user.verify_password(password_form.old_password.data):
			current_user.change_password(password_form.new_password.data)
			db.session.commit()
			flash(u"Nouveau mot de passe enregistré")
			return redirect(url_for('auth.logout'))
		else:
			wrong_password = True

	return render_template('client/settings.html', user=current_user.serialize(),
		password_form = password_form, wrong_password = wrong_password,
		latest_messages=latest_messages)