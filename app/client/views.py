# -*- coding: utf-8 -*-
from . import client

from flask import abort, flash, url_for, render_template,\
				  redirect, request, current_app, jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Subject

from ..decorators import client_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query, room_name

from unidecode import unidecode

import dateutil.parser

from datetime import datetime

from forms import ProfileForm

import json



import logging


logging.basicConfig(filename="/home/arjjuna/flask/compagnon/compagnon/info.log", level=logging.INFO)









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













@client.route('/unread_msgs_number')
def unread_msgs():
	return json.dumps({'n':current_user.unread_msgs}), 200, {'ContentType':'application/json'}





























@client.route('/recherche')
def search():
	"""Where a client looks for profs"""
	latest_messages = current_user.contacts_latest_messages()
	
	keywords = request.args.get('keywords')


	prof_list = Prof.query.all()

	return render_template('client/nsearch.html', user=current_user.serialize(),
							latest_messages=latest_messages, keywords=keywords,
							prof_list=prof_list)




















@client.route('/prof')
def aprof_look():
	latest_messages = current_user.contacts_latest_messages()
	
	return render_template('client/naprof.html', user=current_user.serialize(),
							latest_messages=latest_messages)





















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


