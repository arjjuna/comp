# -*- coding: utf-8 -*-
from . import prof

from flask import abort, flash, url_for, render_template, redirect, request, current_app, \
				  jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Subject, Education, Experience

from ..decorators import prof_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query, room_name, allowed_file

from werkzeug.utils import secure_filename

from datetime import datetime

import json

import os





@prof.before_request
@prof_required
def before_request():
	pass



















@prof.route('/')
def index():
	latest_messages = current_user.contacts_latest_messages()

	return render_template('prof/index.html', user=current_user.serialize(),
	 latest_messages=latest_messages)















@prof.route('/reset_unread', methods=['GET', 'POST'])
def reset_unread():
	if request.method == 'POST':
		current_user.unread_msgs = 0
		db.session.commit()

		return json.dumps({'success':True}), 200, {'ContentType':'application/json'}






@prof.route('/unread_msgs_number')
def unread_msgs():
	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}


















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


























@prof.route('/profile', methods=['GET', 'POST'])
def profile():
	subjects = Subject.query.all()

	latest_messages = current_user.contacts_latest_messages()
	u = current_user

	placeholders = {
		'title': u.prof.title,
		'birth_date': u.birth_date.strftime("%d/%m/%Y"),
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

		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(current_app.config['USERS_UPLOAD_FOLDER'], filename))
			current_user.picture = filename
			db.session.commit()
			flash(u'image enregistrée')
			return redirect(url_for('prof.profile'))

	return render_template('prof/picture_upload.html', user=current_user.serialize(),
	 latest_messages=latest_messages)
