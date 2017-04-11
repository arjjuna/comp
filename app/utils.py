from models import User, Client, Prof, Message

from sqlalchemy import and_, or_

from models import User, Level, Subject, City

from flask import render_template, current_app

from PIL import Image

from datetime import datetime

from app import db

from sqlalchemy import or_, and_

from consts import stop_words_fr

def allowed_file(filename, extensions_set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions_set

def room_name(id1, id2):
	#gives a unique room name for a combinaton of two user ids
	if id1 > id2:
		return str(id2) + "_" + str(id1)
	else:
		return str(id1) + "_" + str(id2)

# These functions are not fully tested
def latest_message(message_list):
	""" Returns the latest message from a list """
	if len(message_list) == 0:
		return None
	message_list.sort(key=lambda x: x.timestamp)
	return message_list[-1]

def message_senders(message_list):
	""" Returns a list of senders from a message list """
	return list(set([m.sender for m in message_list]))





def latest_messages_by_sender(User, n=0):
	all_received = User.messages_received
	all_senders = message_senders(all_received.all())

	latest_by_sender = [
						(s,
						 latest_message(all_received.filter_by(sender=s).all())
						) for s in all_senders]
	if n and len(latest_by_sender) > n:
		return latest_by_sender[:n]
	else:
		return latest_by_sender


def conversation_query(user1, user2):
	conversation = Message.query.filter(or_(
								and_(Message.sender == user1, Message.receiver == user2),
								and_(Message.sender == user2, Message.receiver == user1)
										))

	return conversation.order_by(Message.timestamp.desc())







def crop_image(src, dest, x, y, width, height):
	img = Image.open(src)
	cropped_img = img.crop((x, y, x+width, y+height))
	cropped_img.save(dest)


def crop_first_upload(src, dest):
	img = Image.open(src)
	width = min(img.size)
	height = width

	cropped_img = img.crop((0, 0, width, height))
	cropped_img.save(dest)




def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (datetime(d.year + years, 1, 1) - datetime(d.year, 1, 1))



def search_profs(d):
	"""
		{
			u'age_range': {u'to': 80, u'from': 18},
			u'levels': [u'2'], u'subjects': [u'2', u'3'],
			u'keywords': u'kdjksd ajsk k asd', u'price_range': {u'to': 400, u'from': 50},
			u'cities': [u'3', u'5']}	
	"""

	ps = Prof.query

	#age section
	max_birth_date = add_years(datetime.utcnow(), -d[u'age_range'][u'from'])
	min_birth_date = add_years(datetime.utcnow(), -d[u'age_range'][u'to'])

	users_with_age = db.session.query(User.id).filter(
		and_(User.birth_date < max_birth_date, min_birth_date < User.birth_date)
		).all()

		#SqlAlchemy 'in_' should not be invocked with an empty list
	if users_with_age:
		ps = ps.filter(Prof.user_id.in_(users_with_age))
	else:
		ps = ps.filter(None)

	#price section
	max_price = d[u'price_range'][u'to']
	min_price = d[u'price_range'][u'from']

	ps = ps.filter(and_(Prof.hourly_fee <= max_price, Prof.hourly_fee >= min_price))
	
	#city
	if d[u'cities']:
		cities = db.session.query(City.id).filter(City.id.in_([int(x) for x in d[u'cities']])).all()
		ps = ps.filter(Prof.city_id.in_(cities))

	#levels
	if d[u'levels']:
		levels = db.session.query(Level.id).filter(Level.id.in_([int(x) for x in d[u'levels']])).all()
		ps = ps.filter(Prof.levels.any(Level.id.in_(levels) ) )

	#subjects
	if d[u'subjects']:
		subjects = db.session.query(Subject.id).filter(Subject.id.in_([int(x) for x in d[u'subjects']])).all()
		ps = ps.filter(or_(Prof.principal_subject_id.in_(subjects), Prof.secondary_subject_id.in_(subjects) ))


	ps_list = ps.all()
	

	if d[u'keywords']:
		words = set(d[u'keywords'].lower().split()) - set(stop_words_fr)

		scored_list = []
		for p in ps_list:
			if set(p.user.last_name.lower().split()).intersection(words):
				scored_list += [(p, 100)]

			elif set(p.user.first_name.lower().split()).intersection(words):
				scored_list += [(p, 40)]
			
			elif set(p.title.lower().split()).intersection(words):
				score = 20*len(set(p.title.lower().split()).intersection(words))
				scored_list += [(p, score)]

			elif set((" ".join([x.to_text() for x in p.educations])).split()).intersection(words):
				_n = len(set((" ".join([x.to_text() for x in p.educations])).split()).intersection(words))
				score = _n*15
				scored_list += [(p, score)]
			
			elif set((" ".join([x.to_text() for x in p.experiences])).split()).intersection(words):
				_n = len(set((" ".join([x.to_text() for x in p.experiences])).split()).intersection(words))
				score = _n*15
				scored_list += [(p, score)]

			
			else:
				#scored_list += [(p, 0)]
				pass

		ps_list = [p[0] for p in sorted(scored_list, key=lambda x: x[1], reverse=True)]	

		print ps_list

	
	return ps_list