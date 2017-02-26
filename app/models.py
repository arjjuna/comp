from flask import current_app

from . import db, login_manager

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy import desc

from unidecode import unidecode


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
								db.Column('left_user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
								db.Column('right_user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
								)


class User(UserMixin, db.Model):
	"""User model"""
	__tablename__ = 'users'
	id            = db.Column(db.Integer, primary_key=True)
	email         = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	username      = db.Column(db.String(64))
	first_name    = db.Column(db.String(64))
	last_name     = db.Column(db.String(64), index=True)
	safe_name     = db.Column(db.String(200))
	picture       = db.Column(db.String(500))
	member_since  = db.Column(db.DateTime(), default=datetime.utcnow)
	confirmed     = db.Column(db.Boolean, default=False)
	last_seen     = db.Column(db.DateTime(), default=datetime.utcnow)


	role_id       = db.Column(db.Integer, db.ForeignKey('roles.id'))

	client        = db.relationship('Client', uselist=False, back_populates='user')
	prof          = db.relationship('Prof', uselist=False, back_populates='user')
	
	contacts_right = db.relationship('User', secondary=contact_relation,
									primaryjoin=id==contact_relation.c.left_user_id,
									secondaryjoin=id==contact_relation.c.right_user_id,
									backref="contacts_left")

	messages_sent     = db.relationship('Message', backref='sender',   lazy='dynamic', foreign_keys='Message.from_id')
	messages_received = db.relationship('Message', backref='receiver', lazy='dynamic', foreign_keys='Message.to_id')

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
		return self.messages_sent.filter_by(receiver=to).order_by(desc(Message.timestamp)).first()

	def last_message_received_from(self, _from):
		return self.messages_received.filter_by(sender=_from).order_by(desc(Message.timestamp)).first()

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
			return {'type': 'sent', 'who': latest_sent.receiver,
					'message_obj': latest_sent, 'iso_date': latest_sent.timestamp.isoformat()}
		else: 
			return {'type': 'received', 'who': latest_sent.sender,
					'message_obj': latest_received, 'iso_date': latest_received.timestamp.isoformat()}

	def contacts_latest_messages(self, n=None):
		the_list = [ self.last_contact_with(contact) for contact in self.contacts ]
		the_list.sort(key=lambda x: x['message_obj'].timestamp, reverse=True)
		if n:
			return the_list[:n]
		else:
			return the_list


	
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['APP_ADMIN']:
				self.role = Role.query.filter_by(name='administrator').first()
			if self.role is None:
				self.role = Role.query.filter_by(name='user').first()
			if self.picture is None:
				self.picture = "uploads/users/placeholder.jpg"

		self.safe_name = unidecode(self.first_name + u'_' + self.last_name + u'_' + unicode(self.id))

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

	def __repr__(self):
		return '<Client %s>' % self.id

class Prof(db.Model):
	"""A prof user, with a one-to-one relationship to the users table"""
	__tablename__ = 'profs'

	id            = db.Column(db.Integer, primary_key=True)
	title         = db.Column(db.String(250))

	user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
	user          = db.relationship("User", back_populates="prof")

	def send_message(self, client, text):
		if not client.user.is_client():
			raise MessageRestriction("Prof can only messages to clients")
		message = Message(text=text, sender=self.user, receiver=client.user)
		self.user.contacts_right.append(client.user)
		db.session.add(message)
		db.session.commit()

	def __repr__(self):
		return '<Prof %s>' % self.id

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

	def __repr__(self):
		return '<Message %s>' % self.id


class Subject(db.Model):
	""" Suvjects """
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


class Booking(db.Model):
	__tablename__ = 'bookings'

	id         = db.Column(db.Integer, primary_key=True)
	date       = db.Column(db.DateTime())
	price      = db.Column(db.Integer)
	hours      = db.Column(db.Integer)
	subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	subject    = db.relationship("Subject", backref="bookings")
