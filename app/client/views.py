from . import client

from flask import abort, flash, url_for, render_template, redirect, request, current_app, jsonify

from flask_login import login_required, current_user

from ..models import User, Prof, Client, Message

from ..decorators import client_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query

from unidecode import unidecode


def room_name(id1, id2):
	if id1 > id2:
		return str(id2) + "_" + str(id1)
	else:
		return str(id1) + "_" + str(id2)

@client.before_request
@client_required
def before_request():
	pass



@client.route('/')
def index():
	"""Index of the client side"""
	latest_messages = current_user.contacts_latest_messages()
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nindex.html', user=user, latest_messages=latest_messages)

@client.route('/search')
def search():
	"""Where a client looks for profs"""
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nsearch.html', user=user)

@client.route('/prof')
def aprof_look():
	latest_messages = current_user.contacts_latest_messages()
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/naprof.html', user=user)

@client.route('/prof/<safe_name>')
def aprof(safe_name):
	"""How a client views a prof"""
	latest_messages = current_user.contacts_latest_messages()
	prof_obj = Prof.query.filter(Prof.user == User.query.filter_by(safe_name=safe_name).first()).first()
	
	if not prof_obj:
		abort(404)

	prof_dict = {
		'first_name': prof_obj.user.first_name.title(),
		'last_name': prof_obj.user.last_name.title()
	}

	user = {
		'full_name': current_user.first_name.title() + " " + current_user.last_name.title(),
		'first_name': current_user.first_name.title(),
		'last_name': current_user.last_name.title(),
	}
	return render_template('client/aprof.html', user=user, prof=prof_dict, latest_messages=latest_messages)

@client.route('/reservation')
def booking_look():
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nbooking.html', user=user)

@client.route('/reservation/<safe_name>')
def booking(safe_name):
	"""Where a client makes a booking witht a prof"""
	latest_messages = current_user.contacts_latest_messages()
	prof_obj = Prof.query.filter(Prof.user == User.query.filter_by(safe_name=safe_name).first()).first()

	if not prof_obj:
		abort(404)

	prof_dict = {
		'first_name': prof_obj.user.first_name.title(),
		'last_name': prof_obj.user.last_name.title()
	}
	user = {
		'full_name': current_user.first_name.title() + " " + current_user.last_name.title(),
		'first_name': current_user.first_name.title(),
		'last_name': current_user.last_name.title(),
	}
	return render_template('client/booking.html', user=user, prof=prof_dict, latest_messages=latest_messages)


@client.route('/reservation_handler', methods=['GET', 'POST'])
def booking_handler():
	"""Hadles ajax POST request to make a booking"""
	if request.method == 'POST':
		print request.get_json()
		print type(request.get_json())

		return 'post response'
	else:
		return 'not post response'


@client.route('/reservations')
def my_bookings():
	"""Where a client sees his bookings"""
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nbookings.html', user=user)

@client.route('/valider')
def validate_booking():
	"""Where a client validates the booking (when the prof has done his job)"""
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nvalidate.html', user=user)

@client.route('/chat')
def chat_template():
	latest_messages = current_user.contacts_latest_messages()
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nchat.html', user=user, latest_messages=latest_messages)

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


@client.route('/chat/<safe_name>')
def chat(safe_name):
	"""a chat view"""
	latest_messages = current_user.contacts_latest_messages()
	prof_obj = Prof.query.filter(Prof.user == User.query.filter_by(safe_name=safe_name).first()).first()

	if not prof_obj:
		abort(404)

	prof_dict = {
		'id': prof_obj.user.id,
		'first_name': prof_obj.user.first_name.title(),
		'last_name': prof_obj.user.last_name.title()
	}
	user = {
		'id': current_user.id,
		'full_name': current_user.first_name.title() + " " + current_user.last_name.title(),
		'first_name': current_user.first_name.title(),
		'last_name': current_user.last_name.title(),
	}

	return render_template('client/chat.html', user=user, prof=prof_dict,
							latest_messages=latest_messages, safe_name=safe_name)



