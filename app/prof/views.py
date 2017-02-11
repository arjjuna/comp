from . import prof

from flask import abort, flash, url_for, render_template, redirect, request, current_app

from flask_login import login_required, current_user

from ..models import User, Prof, Client, Message

from ..decorators import prof_required

from sqlalchemy import or_


def room_name(id1, id2):
	if id1 > id2:
		return str(id2) + "_" + str(id1)
	else:
		return str(id1) + "_" + str(id2)

@prof.before_request
@prof_required
def before_request():
	pass

@prof.route('/')
def index():
	return render_template('prof/index.html')


@prof.route('/chat/with/<int:client_id>')
def chat_with(client_id):
	_from  = current_user
	_to    = Client.query.get(client_id).user
	messages = Message.query.filter(or_(Message.receiver==_to,
										Message.sender==_to)).filter(or_(Message.receiver==_from, 
																		 Message.sender==_from)).all()
	messages.sort(key=lambda x: x.timestamp)
	return render_template('client/chat.html', messages=messages,
						   _from=_from, _to=_to,
						   room_name=room_name(_from.id, _to.id))

