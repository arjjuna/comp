from .. import db

from ..models import User, Prof, Client, Message

def save_message_from_dict(message_dict):
	"""
		{u'to_id': u'5', u'message': u'adasd', u'room': u'4_5', u'from_id': u'4'}
	"""

	message = Message(text=message_dict['message'],
					  sender=User.query.get(message_dict['from_id']),
					  receiver=User.query.get(message_dict['to_id']))

	db.session.add(message)
	db.session.commit()

	return True