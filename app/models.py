# -*- coding: utf-8 -*-
from flask import current_app, url_for

from . import db, login_manager

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash	
from werkzeug import  secure_filename
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy import desc
from sqlalchemy.orm import backref

from unidecode import unidecode

from datetime import date, datetime

import json

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


class Permission:
	"""A binary representation of permissions.
	Can sum two permissions (example: 0b001+0b100 = 0b101)"""
	EDIT_SELF  = 0b000001
	ADMINISTER = 0b100000

class Role(db.Model):
	"""Users roles, simple user or admin (not to confuse with Client, Prof)"""
	__tablename__ = 'roles'

	id            = db.Column(db.Integer, primary_key=True)
	name          = db.Column(db.String(64), unique=True)
	default       = db.Column(db.Boolean, default=False)
	permissions   = db.Column(db.Integer)

	users         = db.relationship('User', backref='role')

	@staticmethod
	def insert_roles():
		"""Insert pre-defined roles in the database"""
		roles = {
			'simple_user': (Permission.EDIT_SELF, True),
			'administrator': (Permission.ADMINISTER, False)
		}

		for r in roles:
			role = Role.query.filter_by(name=r).first()
			if role is None:
				role = Role(name=r,
							permissions= roles[r][0],
							default= roles[r][1]
							)

				db.session.add(role)
				db.session.commit()

	def __repr__(self):
		return '<role %s>' % self.name

contact_relation = db.Table('contacts_table',
								db.Column('left_user_id', db.Integer, db.ForeignKey('users.id'),
										  primary_key=True),
								db.Column('right_user_id', db.Integer, db.ForeignKey('users.id'),
										  primary_key=True)
								)











class ChatStatus(db.Model):
	__tablename__ = "chat_statuses"
	id            = db.Column(db.Integer, primary_key=True)
	name          = db.Column(db.String(64))
	name_fr       = db.Column(db.String(64))
	code          = db.Column(db.Integer)

	@staticmethod
	def insert_statuses():
		statuses = {
			"offline": ["hors ligne", 0b000000],
			"online": ["en ligne", 0b100000],
			"busy": ["occupé", 0b010000],
		}

		for s in statuses:
			status = ChatStatus.query.filter_by(name=s).first()
			if status is None:
				status = ChatStatus(
					name    = s,
					name_fr = statuses[s][0],
					code = statuses[s][1]
					)

				db.session.add(status)
				db.session.commit()


	def __repr__(self):
		return "<status {0}>".format(name)













class User(UserMixin, db.Model):
	"""User model"""
	__tablename__ = 'users'
	id            = db.Column(db.Integer, primary_key=True)
	
	email         = db.Column(db.String(64), unique=True) #can change
	password_hash = db.Column(db.String(128)) #can change
	old_pass_hash = db.Column(db.String(128)) #can change
	username      = db.Column(db.String(64))
	
	first_name    = db.Column(db.String(64))
	last_name     = db.Column(db.String(64), index=True)
	safe_name     = db.Column(db.String(200))
	
	picture       = db.Column(db.String(500), default="placeholder.jpg") #can edit
	original_picture = db.Column(db.String(500)) #can edit
	
	birth_date    = db.Column(db.DateTime())

	member_since  = db.Column(db.DateTime(), default=datetime.utcnow)
	confirmed     = db.Column(db.Boolean, default=False)
	last_seen     = db.Column(db.DateTime(), default=datetime.utcnow)

	unread_msgs          = db.Column(db.Integer, default=0)
	unread_notifications = db.Column(db.Integer, default=0)

	status_id     = db.Column(db.Integer, db.ForeignKey('chat_statuses.id'))
	status        = db.relationship('ChatStatus', backref='users', foreign_keys=[status_id])


	
	default_status_id     = db.Column(db.Integer, db.ForeignKey('chat_statuses.id'))
	default_status        = db.relationship('ChatStatus', backref='users_with_default', foreign_keys=[default_status_id])



	role_id       = db.Column(db.Integer, db.ForeignKey('roles.id'))

	client        = db.relationship('Client', uselist=False, back_populates='user')
	prof          = db.relationship('Prof', uselist=False, back_populates='user')
	
	contacts_right = db.relationship('User', secondary=contact_relation,
									primaryjoin=id==contact_relation.c.left_user_id,
									secondaryjoin=id==contact_relation.c.right_user_id,
									backref="contacts_left")

	messages_sent     = db.relationship('Message', backref='sender',lazy='dynamic',
										foreign_keys='Message.from_id')
	messages_received = db.relationship('Message', backref='receiver', lazy='dynamic',
										foreign_keys='Message.to_id')

	@property
	def age(self):
		return calculate_age(self.birth_date)

	@property
	def contacts(self):
		return list(set(self.contacts_right + self.contacts_left))

	@contacts.setter
	def contacts(self, value):
		raise AttributeError("Contacts can't be set. Check contacts_right and contacts_left")

	@contacts.deleter
	def contacts(self):
		raise AttributeError("Contacts can't be deleted. Check contacts_right and contacts_left")


	#Password is proprety that can't be accessed
	@property
	def password(self):
		raise AttributeError("password is not a readable attribute")

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def change_password(self, new_password):
		self.old_pass_hash = self.password_hash
		self.password_hash = generate_password_hash(new_password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)
		
	def generate_confirmation_token(self, expiration=12*3600):
		s = Serializer(current_app.config['SECRET_KEY'], expiration)
		return s.dumps({'confirm': self.id})
	
	def confirm(self, token):
		s = Serializer(current_app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except:
			return False
		if data.get('confirm') != self.id:
			return False
		self.confirmed = True
		db.session.add(self)
		db.session.commit()
		return True
		
	def can(self, permissions):
		# Check's if a user has a certain permission
		return self.role is not None and \
			(self.role.permissions & permissions) == permissions
	
	def is_administrator(self):
		# Checks  if the user is an administrator
		return self.role.name == 'administrator'

	def is_client(self):
		return self.client != None

	def is_prof(self):
		return self.prof != None

	def is_anonymous(self):
		return False


	def last_message_sent_to(self, to):
		return self.messages_sent.filter_by(receiver=to).order_by(
																  desc(Message.timestamp)
																 ).first()

	def last_message_received_from(self, _from):
		return self.messages_received.filter_by(sender=_from).order_by(
																	    desc(Message.timestamp)
																	  ).first()

	def last_contact_with(self, other):
		latest_sent = self.last_message_sent_to(other)
		latest_received = self.last_message_received_from(other)

		if latest_sent is None:
			if latest_received is None:
				return None
			else:
				return latest_received
		elif latest_received is None:
			return latest_sent

		# We can be sure that both are not none 

		if latest_sent.timestamp > latest_received.timestamp:
			return {
					'type': 'sent',
					'who': latest_sent.receiver,
					'message_obj': latest_sent,
					'iso_date': latest_sent.timestamp.isoformat()
					}
		else: 
			return {
					'type': 'received',
					'who': latest_received.sender,
					'message_obj': latest_received,
					'iso_date': latest_received.timestamp.isoformat()
					}

	def contacts_latest_messages(self, n=None):
		the_list = [ self.last_contact_with(contact) for contact in self.contacts ]
		the_list.sort(key=lambda x: x['message_obj'].timestamp, reverse=True)
		if n:
			return the_list[:n]
		else:
			return the_list

	def chat_link(self):
		chat_link = ''
		if self.is_prof():
			chat_link = url_for('client.chat', safe_name=self.safe_name)
		elif self.is_client():
			chat_link = url_for('prof.chat', safe_name=self.safe_name)

		return chat_link

	def picture_link(self):
		picture_link = url_for('main.profile_picture', filename=self.picture)
		return picture_link


	def serialize(self):

		return {
				'id': self.id,
				'full_name': self.first_name.title() + " " + self.last_name.title(),
				'first_name': self.first_name.title(),
				'last_name': self.last_name.title(),
				'profile_picture': self.picture,
				'original_picture': self.original_picture,
				'chat_link': self.chat_link(),
				'picture_link': self.picture_link()
				}

	
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['APP_ADMIN']:
				self.role = Role.query.filter_by(name='administrator').first()
			if self.role is None:
				self.role = Role.query.filter_by(name='user').first()
			if self.picture is None:
				self.picture = "uploads/users/placeholder.jpg"

		#Added "secure_filename" part without testing
		self.safe_name = secure_filename(unidecode(self.first_name + u'_' + \
							self.last_name + u'_' + unicode(self.id))).lower()

	def __repr__(self):
		return '<User %r, email: %r>' % (self.username, self.email)
		
class AnonymousUser(AnonymousUserMixin):
	# Anonymous user, requirement of the Flask-login extension
	def can(self, permission):
		return False
	def is_administrator(self, permission):
		return False
	def is_client(self):
		return False
	def is_prof(self):
		return False
	def is_anonymous(self):
		return True

# Set the flask_login anonymous user to the custom one
login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
	# User loader, requirement of the Flask-login extension
	return User.query.get(int(user_id))























class Subject(db.Model):
	""" Subjects """
	__tablename__ = 'subjects'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)

	@staticmethod
	def insert_subjects():
		subjects = ['maths', 'physique', 'SVT']

		for s in subjects:
			one_subject = Subject.query.filter_by(name=s).first()
			if not one_subject: 
				one_subject = Subject(name=s)
				db.session.add(one_subject)

		db.session.commit()

	def url_safe_name(self):
		return secure_filename(unidecode(self.name.lower()))

	def __repr__(self):
		return ('<Subject %s, %s>' % (self.id, self.name)).encode('utf-8')







"""Association table for the many-to-many relation between profs and levels"""
levels_prof_relation = db.Table('levels_profs', db.Model.metadata,
		db.Column('level_id', db.Integer, db.ForeignKey('levels.id')),
		db.Column('prof_id', db.Integer, db.ForeignKey('profs.id'))
	)





class Level(db.Model):
	""" Levels """
	__tablename__ = 'levels'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)



	@staticmethod
	def insert_levels():
		levels = ['collège', 'lycée', 'primaire']

		for l in levels:
			one_level = Level.query.filter_by(name=l).first()
			if not one_level: 
				one_level = Level(name=l)
				db.session.add(one_level)

		db.session.commit()

	def __repr__(self):
		return ('<Level %s, %s>' % (self.id, self.name)).encode('utf-8')























class MessageRestriction(Exception):
	"""Error raised when the message sender is not allowed to contact the receiver""" 
	def __init__(self, message, *args):
		self.message = message

		super(MessageRestriction, self).__init__(message, *args)

class Client(db.Model):
	"""A client user, with a one-to-one relationship to the users table"""
	__tablename__ = 'clients'

	id            = db.Column(db.Integer, primary_key=True)
	about_me      = db.Column(db.String(250))



	user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
	user          = db.relationship("User", back_populates="client")

	def send_message(self, prof, text):
		if not prof.user.is_prof():
			raise MessageRestriction("Client can only messages to profs")
		message = Message(text=text, sender=self.user, receiver=prof.user)
		self.user.contacts_right.append(prof.user)
		db.session.add(message)
		db.session.commit()

	def serialize(self):
		return {
				'id': self.id,
				'first_name': self.user.first_name.title(),
				'last_name': self.user.last_name.title(),
				'profile_picture': self.user.picture,
				'user_id': self.user.id
				}


	def __repr__(self):
		return '<Client %s, (%s %s)>' % (self.id, self.user.first_name, self.user.last_name)




class Prof(db.Model):
	"""A prof user, with a one-to-one relationship to the users table"""
	__tablename__ = 'profs'

	id            = db.Column(db.Integer, primary_key=True)
	title         = db.Column(db.String(250))

	hourly_fee    = db.Column(db.Integer)

	city_id       = db.Column(db.Integer, db.ForeignKey('cities.id'))
	city          = db.relationship("City", backref="profs" )


	user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
	user          = db.relationship("User", back_populates="prof")

	about_me      = db.Column(db.String(2500))

	principal_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	principal_subject = db.relationship("Subject", backref="principal_profs",
										foreign_keys=[principal_subject_id])
	
	secondary_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	secondary_subject    = db.relationship("Subject", backref="secondary_profs",
										foreign_keys=[secondary_subject_id])


	educations = db.relationship("Education", back_populates="prof")
	experiences = db.relationship("Experience", back_populates="prof")

	levels = db.relationship("Level", secondary=levels_prof_relation, backref="levels")

	@property
	def subjects(self):
		return [self.principal_subject, self.secondary_subject]
	
	@subjects.setter
	def subjects(self, value):
		raise AttributeError("Subjects can't be set. Check principal_subject " + \
							 "and secondary_subject")

	@subjects.deleter
	def subjects(self):
		raise AttributeError("Subjects can't be set. Check principal_subject " + \
							 "and secondary_subject")

	def send_message(self, client, text):
		if not client.user.is_client():
			raise MessageRestriction("Prof can only messages to clients")
		message = Message(text=text, sender=self.user, receiver=client.user)
		self.user.contacts_right.append(client.user)
		db.session.add(message)
		db.session.commit()

	def serialize(self):
		return {
				'id': self.id,
				'first_name': self.user.first_name.title(),
				'last_name': self.user.last_name.title(),
				'safe_name': self.user.safe_name,
				'profile_picture': self.user.picture,
				'title': self.title,
				'subjects' : [s.name.title() for s in self.subjects],
				'user_id': self.user.id,
				'age': self.user.age,
				'city': self.city.name.title(),
				'hourly_fee': self.hourly_fee,
				'about_me': self.about_me,
				'educations': self.educations,
				'experiences': self.experiences
				}

	def __repr__(self):
		return '<Prof {0}, ({1} {2})>'.format(self.id, self.user.first_name.encode('utf-8'), self.user.last_name.encode('utf-8'))










class Education(db.Model):
	__tablename__ = "educations"
	id            = db.Column(db.Integer, primary_key=True)
	title         = db.Column(db.String(250))
	school        = db.Column(db.String(250))
	start         = db.Column(db.DateTime())
	end           = db.Column(db.DateTime())
	is_current  = db.Column(db.Boolean, default=False)
	description   = db.Column(db.String(2500))
	prof_id       = db.Column(db.Integer, db.ForeignKey('profs.id'))
	prof          = db.relationship("Prof", back_populates="educations")

	def to_text(self):
		return (self.title + " " + self.description + " " + self.school).lower()

	def start_repr(self, month_letters=False):
		if not self.start or (self.start==""):
			return ""
		if month_letters:
			return unicode(datetime.strftime(self.start, "%B %Y"), 'utf-8')
		return unicode(datetime.strftime(self.start, "%m/%Y"), 'utf-8')
	
	def end_repr(self, month_letters=False):
		if not self.end or (self.end==""):
			return ""
		if month_letters:
			return unicode(datetime.strftime(self.end, "%B %Y"), 'utf-8')
		return unicode(datetime.strftime(self.end, "%m/%Y"), 'utf-8')


	def __repr__(self):
		return "<education: {0}, prof_id: {1}>".format(self.title, str(self.prof_id))



class Experience(db.Model):
	__tablename__ = "experiences"
	id            = db.Column(db.Integer, primary_key=True)
	position    = db.Column(db.String(250))
	company     = db.Column(db.String(250))
	start       = db.Column(db.DateTime())
	end         = db.Column(db.DateTime())
	is_current  = db.Column(db.Boolean, default=False)
	description = db.Column(db.String(2500))
	prof_id     = db.Column(db.Integer, db.ForeignKey('profs.id'))
	prof        = db.relationship("Prof", back_populates="experiences")


	def to_text(self):
		return (self.position + " " + self.description + " " + self.company).lower()

	def start_repr(self, month_letters=False):
		if not self.start or (self.start==""):
			return ""
		if month_letters:
			return unicode(datetime.strftime(self.start, "%B %Y"), 'utf-8')
		return unicode(datetime.strftime(self.start, "%m/%Y"), 'utf-8')
	
	def end_repr(self, month_letters=False):
		if not self.end or (self.end==""):
			return ""
		if month_letters:
			return unicode(datetime.strftime(self.end, "%B %Y"), 'utf-8')
		return unicode(datetime.strftime(self.end, "%m/%Y"), 'utf-8')


	def __repr__(self):
		return "<experience: {0}, prof_id: {1}>".format(self.title, str(self.prof_id))



















class Message(db.Model):
	"""Message model"""
	__tablename__ = 'messages'
	id            = db.Column(db.Integer, primary_key=True)
	text          = db.Column(db.String(2500))
	timestamp     = db.Column(db.DateTime(), default=datetime.utcnow)
	seen          = db.Column(db.Boolean, default=False)

	from_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
	to_id         = db.Column(db.Integer, db.ForeignKey('users.id'))

	def to_dict(self):
		return {
			'id': str(self.id),
			'text': self.text,
			'timestamp': self.timestamp.isoformat(),
			'seen': str(self.seen),
			'from_id': str(self.from_id),
			'to_id': str(self.to_id)
		}

	def serialize(self):
		d = {
			'text': self.text,
			'timestamp': str(self.timestamp.isoformat()),
			'seen': 1*self.seen + 0,
			'from_id': str(self.from_id),
			'to_id': str(self.to_id)
		}

		return d

	def __repr__(self):
		return '<Message %s>' % self.id




















class City(db.Model):
	__tablename__ = "cities"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))

	@staticmethod
	def insert_cities():
		from consts import cities
		for c in cities:
			city = City.query.filter_by(name=c).first()
			if city is None:
				city = City(name=c)
				db.session.add(city)
		db.session.commit()

	def __repr__(self):
		return "<city: {0}>".format(self.name)



















class Notification(db.Model):
	__tablename__ = "notifications"
	id            = db.Column(db.Integer, primary_key=True)
	text          = db.Column(db.String(1000))

	picture          = db.Column(db.String(500))
	picture_endpoint = db.Column(db.String(100))
	picture_kwargs   = db.Column(db.String(500))

	link          = db.Column(db.String(500))
	link_endpoint = db.Column(db.String(100))
	link_kwargs   = db.Column(db.String(500))


	timestamp     = db.Column(db.DateTime(), default=datetime.utcnow)


	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	user    = db.relationship('User', backref="notifications")

	def generate_link(self, endpoint, kwargs_json):
		return url_for(endpoint, **json.loads(kwargs_json))

	def get_picture(self):
		if self.picture:
			return self.picture
		else:
			return self.generate_link(self.picture_endpoint, self.picture_kwargs)

	def get_link(self):
		if self.link:
			return self.link
		else:
			return self.generate_link(self.link_endpoint, self.link_kwargs)


	def serialize(self):
		d = {
				'text'     : self.text,
				'picture'  : self.get_picture(),
				'link'     : self.get_link(),
				'timestamp': str(self.timestamp.isoformat()),
			}

		return d


	def __repr__(self):
		return "<notification: {0}>".format(self.id)

	def __init__(self, **kwargs):
		super(Notification, self).__init__(**kwargs)
		if not self.user.unread_notifications:
			self.user.unread_notifications = 1
		else:
			self.user.unread_notifications += 1





















