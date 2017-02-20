from . import client

from flask import abort, flash, url_for, render_template, redirect, request, current_app

from flask_login import login_required, current_user

from ..models import User, Prof, Client, Message

from ..decorators import client_required

from sqlalchemy import or_

from ..utils import latest_messages_by_sender


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
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nindex.html', user=user)

@client.route('/search')
def search():
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/nsearch.html', user=user)

@client.route('/prof')
def aprof():
	latest_messages = latest_messages_by_sender(current_user, 4)
	user = {
		'full_name': current_user.first_name + " " + current_user.last_name,
		'first_name': current_user.first_name,
		'last_name': current_user.last_name,
	}
	return render_template('client/naprof.html', user=user)


# Non workin view, just shows the chat looks
@client.route('/chat_looks')
def chat_looks():
	return render_template('client/chat_looks.html')

@client.route('/chat/with/<int:prof_id>')
def chat_with(prof_id):
	_from  = current_user
	_to    = Prof.query.get(prof_id).user
	messages = Message.query.filter(or_(Message.receiver==_to,
										Message.sender==_to)).filter(or_(Message.receiver==_from, 
																		 Message.sender==_from)).all()
	messages.sort(key=lambda x: x.timestamp)
	return render_template('client/chat.html', messages=messages,
						   _from=_from, _to=_to,
						   room_name=room_name(_from.id, _to.id))

