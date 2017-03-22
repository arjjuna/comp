from . import prof

from flask import abort, flash, url_for, render_template, redirect, request, current_app, \
				  jsonify, Response

from flask_login import login_required, current_user

from .. import db

from ..models import User, Prof, Client, Message, Booking

from ..decorators import prof_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender, conversation_query, room_name








@prof.before_request
@prof_required
def before_request():
	pass



















@prof.route('/')
def index():
	latest_messages = current_user.contacts_latest_messages()

	return render_template('prof/index.html', user=current_user.serialize(),
	 latest_messages=latest_messages)















@prof.route('/demandes')
def my_bookings():

	bookings = Booking.query.filter(Booking.prof == current_user.prof,
									Booking.client_validated.is_(False),
									Booking.client_canceled.is_(False),
									Booking.prof_accepted.is_(False),
									Booking.prof_declined.is_(False)
									).all()


	return render_template('prof/bookings.html', user=current_user.serialize(),
						   latest_messages = current_user.contacts_latest_messages(),
							bookings=bookings
							)




@prof.route('/seances')
def my_meetings():

	bookings = Booking.query.filter(Booking.prof == current_user.prof,
									Booking.client_validated.is_(False),
									Booking.client_canceled.is_(False),
									Booking.prof_accepted.is_(True),
									Booking.prof_declined.is_(False)
									).all()


	return render_template('prof/meetings.html', user=current_user.serialize(),
						   latest_messages = current_user.contacts_latest_messages(),
							bookings=bookings
							)





@prof.route('/reservation/accept', methods=['GET', 'POST'])
def accept_booking():
	if request.method == 'POST':
		booking_data = request.get_json()
		booking = Booking.query.get(booking_data['id'])

		if not booking:
			abort(404)

		success, status_code = booking.prof_accept(current_user)

		if not success:
			abort(status_code)

		resp = Response("")
		resp.status_code = status_code
		resp.headers['location'] = url_for('prof.my_bookings')

		return resp

	else:
		return "get"




@prof.route('/reservation/decline', methods=['GET', 'POST'])
def decline_booking():
	if request.method == 'POST':
		booking_data = request.get_json()
		booking = Booking.query.get(booking_data['id'])

		if not booking:
			abort(404)

		success, status_code = booking.prof_decline(current_user)

		if not success:
			abort(status_code)

		resp = Response("")
		resp.status_code = status_code
		resp.headers['location'] = url_for('prof.my_bookings')

		return resp

	else:
		return "get"






















@prof.route('/reservations/historique')
def bookings_history():

	bookings = Booking.query.filter(Booking.prof == current_user.prof,
									).all()


	return render_template('prof/bookings_history.html', user=current_user.serialize(),
						   latest_messages = current_user.contacts_latest_messages(),
							bookings=bookings
							)































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



















@prof.route('/chat/<safe_name>')
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