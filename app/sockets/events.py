from flask import g, session

from .. import socketio
from .. import db

from flask_socketio import join_room
from ..models import User, Message

from ..tasks import save_message_from_dict

from flask_login import current_user



"""
@socketio.on('join')
def joinRoom(data):
	print '########## Joined room %s' % data['room']

	print "room: %s created" % data['room']
	join_room(data['room'])
"""

@socketio.on('join')
def joinRoom(data):

	join_room(data['room'])

	current_user.unread_msgs = 0
	db.session.commit()
	#print "####################################\nroom joined"
	#print data['room']


@socketio.on('msg_to_server')
def receive_message(data):
	res = save_message_from_dict.delay(data)
	#print "######################### emitting"
	res.get(timeout = 1)
	socketio.emit('msg_from_server', data, room=data['room'], broadcast=True)

@socketio.on('received_one_msg')
def foo(data):
	User.query.get(data['receiver']).unread_msgs = 0
	m = Message.query.filter_by(
		receiver = User.query.get(data['receiver']),
		sender   = User.query.get(data['sender'])
		).order_by(Message.id.desc()).first()
	m.seen = True
	db.session.commit()