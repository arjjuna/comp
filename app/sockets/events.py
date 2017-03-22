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
	print "####################################\nroom joined"
	print data['room']


@socketio.on('msg_to_server')
def receive_message(data):
	#save_message_from_dict.delay(data)
	print "######################### emitting"
	socketio.emit('msg_from_server', data, room=data['room'], broadcast=True)

@socketio.on('my_event')
def foo(data):
	print '000000000000000'