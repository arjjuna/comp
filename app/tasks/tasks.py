from .. import db, celery

from ..models import User, Prof, Client, Message

import time

from flask_login import current_user







@celery.task
def save_message_from_dict(message_dict):
	from ..wsgi_aux import app
	
	with app.app_context():

		message = Message(text=message_dict['text'], #used to be 'message' instead of text
						  sender=User.query.get(message_dict['from_id']),
						  receiver=User.query.get(message_dict['to_id']))

		User.query.get(message_dict['to_id']).unread_msgs += 1

		db.session.add(message)
		db.session.commit()
		#db.session.expunge_all()

	return True