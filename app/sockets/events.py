from flask import g, session

from .. import socketio

from flask_socketio import join_room
from ..models import Message

from ..tasks import save_message_from_dict



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


@socketio.on('msg_out')
def receive_message(data):
	save_message_from_dict.delay(data)
	socketio.emit('msg_in', data, room=data['room'], broadcast=True)