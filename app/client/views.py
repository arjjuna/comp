from . import client

from flask import abort, flash, url_for, render_template,\
				  redirect, request, current_app, jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Subject, Booking

from ..decorators import client_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query, room_name

from unidecode import unidecode

import dateutil.parser

from forms import ProfileForm




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










@client.route('/reservation')
def booking_look():
	latest_messages = current_user.contacts_latest_messages()
	
	return render_template('client/nbooking.html', user=current_user.serialize(),
							latest_messages=latest_messages)





















@client.route('/reservation/<safe_name>')
def booking(safe_name):
	"""Where a client makes a booking witht a prof"""
	latest_messages = current_user.contacts_latest_messages()
	prof_obj = Prof.query.filter(
								Prof.user == User.query.filter_by(
									safe_name=safe_name
									).first()
								).first()

	if not prof_obj:
		abort(404)

	return render_template('client/booking.html', user=current_user.serialize(),
							prof=prof_obj.serialize(), latest_messages=latest_messages,
							safe_name=safe_name)












@client.route('/booking_handler', methods=['GET', 'POST'])
def booking_handler():
	"""Hadles ajax POST request to make a booking"""
	if request.method == 'POST':
		booking_data = request.get_json()

		success, status_code = current_user.client.make_booking(
								date    = dateutil.parser.parse(booking_data['date']),
								price   = int(booking_data['price']),
								hours   = int(booking_data['hours']),
								subject = Subject.query.get(int(booking_data['subject'])),
								message = booking_data['message'],
								prof    = Prof.query.get(int(booking_data['prof_id']))
								)

		if not success:
			abort(status_code)

		resp = Response("")
		resp.status_code = status_code
		resp.headers['location'] = url_for('client.my_bookings')

		return resp

	else:
		return ""










@client.route('/cancelation', methods=['GET', 'POST'])
def booking_cancel():
	if request.method == 'POST':
		booking_data = request.get_json()

		booking = Booking.query.get(booking_data['id'])

		if not booking:
			abort(404)

		success, status_code = booking.client_cancel(current_user)
		
		if not success:
			abort(status_code)


		
		resp = Response("Booking {0} canceled".format(booking_data['id']))
		resp.status_code = status_code
		resp.headers['location'] = url_for('client.my_bookings')

		return resp


	else:
		return "get"



















@client.route('/reservations')
def my_bookings():
	"""Where a client sees his bookings"""
	latest_messages = current_user.contacts_latest_messages()

	#The bookings made by the current client
	bookings = Booking.query.filter(
		Booking.client          == current_user.client,
		Booking.client_canceled.is_(False),
		Booking.client_validated.is_(False)
		)

	return render_template('client/bookings.html', user=current_user.serialize(),
							latest_messages=latest_messages, bookings=bookings)


















@client.route('/valider')
def validate_booking_look():
	"""Where a client validates the booking (when the prof has done his job)"""
	latest_messages = current_user.contacts_latest_messages()

	return render_template('client/nvalidate.html', latest_messages=latest_messages, 
							user=current_user.serialize())























@client.route('/valider/<int:id_>')
def validate_booking(id_):
	"""Where a client validates the booking (when the prof has done his job)"""
	latest_messages = current_user.contacts_latest_messages()

	booking = Booking.query.get(int(id_))

	if not booking:
		abort(404)

	if booking.client != current_user.client:
		abort(400)

	return render_template('client/validate.html', user=current_user.serialize(),
							latest_messages=latest_messages, booking=booking)























@client.route('/validation', methods=['GET', 'POST'])
def booking_validate():
	if request.method == 'POST':
		booking_data = request.get_json()
		booking = Booking.query.get(booking_data['id'])

		if not booking:
			abort(404)

		success, status_code = booking.client_validate(
							current_user,
							score=int(booking_data['stars']),
							message=booking_data['message']
							)

		if not success:
			abort(status_code)
		
		resp = Response("Booking {0} canceled".format(booking_data['id']))
		resp.status_code = status_code
		resp.headers['location'] = url_for('client.my_bookings')

		return resp

	else:
		return "get"
























@client.route('/reservations/historique')
def bookings_history():
	"""Where a client sees his bookings"""
	latest_messages = current_user.contacts_latest_messages()

	#The bookings made by the current client
	bookings = Booking.query.filter(
		Booking.client          == current_user.client,
		)

	return render_template('client/bookings_history.html', user=current_user.serialize(),
							latest_messages=latest_messages, bookings=bookings)















@client.route('/chat')
def chat_template():
	latest_messages = current_user.contacts_latest_messages()

	return render_template('client/nchat.html', user=current_user.serialize(),
							latest_messages=latest_messages)






















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

	profile_form = ProfileForm()

	if profile_form.validate_on_submit():
		return 'submit'

	return render_template('client/profile.html', user=current_user.serialize(),
							latest_messages=latest_messages, profile_form=profile_form)