from flask import current_app

from . import db, login_manager

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from sqlalchemy import desc
from sqlalchemy.orm import backref

from unidecode import unidecode

from datetime import date

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
	
	picture       = db.Column(db.String(500)) #can edit
	
	birth_date    = db.Column(db.DateTime())

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

	def serialize(self):
		return {
				'id': self.id,
				'full_name': self.first_name.title() + " " + self.last_name.title(),
				'first_name': self.first_name.title(),
				'last_name': self.last_name.title(),
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

		self.safe_name = unidecode(self.first_name + u'_' + \
							self.last_name + u'_' + unicode(self.id))

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

	def __repr__(self):
		return '<Subject %s, %s>' % (self.id, self.name)























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
				'user_id': self.user.id
				}

	def make_booking(self, date, price, hours, subject, message, prof):
		booking = Booking(client  = self,
						  date    = date,
						  price   = price,
						  hours   = hours,
						  subject = subject,
						  message = message,
						  prof    = prof
						  )

		db.session.add(booking)
		db.session.commit()

		return True, 201 # REssource created


	def __repr__(self):
		return '<Client %s, (%s %s)>' % (self.id, self.user.first_name, self.user.last_name)




class Prof(db.Model):
	"""A prof user, with a one-to-one relationship to the users table"""
	__tablename__ = 'profs'

	id            = db.Column(db.Integer, primary_key=True)
	title         = db.Column(db.String(250))

	user_id       = db.Column(db.Integer, db.ForeignKey('users.id'))
	user          = db.relationship("User", back_populates="prof")

	principal_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	principal_subject = db.relationship("Subject", backref="principal_profs",
										foreign_keys=[principal_subject_id])
	
	secondary_subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	secondary_subject = db.relationship("Subject", backref="secondary_profs",
										foreign_keys=[secondary_subject_id])

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
				'subjects' : self.subjects,
				'user_id': self.user.id
				}

	def __repr__(self):
		return '<Prof {0}, ({1} {2})>'.format(self.id, self.user.first_name.encode('utf-8'), self.user.last_name.encode('utf-8'))


























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

























class Booking(db.Model):
	__tablename__ = 'bookings'

	id         = db.Column(db.Integer, primary_key=True)
	date       = db.Column(db.DateTime())
	price      = db.Column(db.Integer)
	hours      = db.Column(db.Integer)
	message    = db.Column(db.String(2500))
	subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
	subject    = db.relationship("Subject", backref="bookings")

	prof_id   = db.Column(db.Integer, db.ForeignKey('profs.id'))
	prof      = db.relationship("Prof", backref="bookings")
	client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
	client    = db.relationship("Client", backref="bookings")


	prof_declined   = db.Column(db.Boolean, default=False) 
	prof_accepted   = db.Column(db.Boolean, default=False)
	
	client_canceled  = db.Column(db.Boolean, default=False)
	client_validated = db.Column(db.Boolean, default=False)

	commented  = db.Column(db.Boolean, default=False)

	score            = db.Column(db.Integer)
	feedback_message = db.Column(db.String(1000))

	@property
	def total(self):
		return self.price*self.hours

	@total.setter
	def total(self, value):
		raise AttributeError("Total can't be set")

	@total.deleter
	def total(self):
		raise AttributeError("Total can't be deleted")

	@property
	def past_due(self):
		return (datetime.utcnow() > self.date)

	@past_due.setter
	def past_due(self, value):
		AttributeError("Past_due can't be set")

	@past_due.deleter
	def past_due(self, value):
		AttributeError("Past_due can't be deleted")

	def no_response(self):
		return (not self.prof_accepted and not self.prof_declined)

	def prof_decline(self, prof_user):
		if self.prof.user == prof_user:
			if self.prof_accepted or self.client_canceled or self.client_validated:
				return False, 400 #Bad Request

			else:
				self.prof_declined = True
				db.session.commit()
				return True, 200 #OK
		else:
			return False, 403 #Forbidden

	def prof_accept(self, prof_user):
		if self.prof.user == prof_user:
			if self.prof_declined or self.client_canceled or self.client_validated:
				return False, 400 #Bad Request

			else:
				self.prof_accepted = True
				db.session.commit()
				return True, 200 #OK
		else:
			return False, 403 #Forbidden

	def client_cancel(self, client_user):
		if self.client.user == client_user:
			if self.prof_declined or self.prof_accepted or self.client_validated:
				return False, 400 #bad request

			else:
				self.client_canceled = True
				db.session.commit()
				return True, 200 #OK
		else:
			return False, 403 #Forbidden

	def client_validate(self, client_user, score, message):
		if self.client.user == client_user:
			if self.prof_declined or not self.prof_accepted or self.client_canceled:
				return False, 400 #Bad request

			else:
				self.client_validated = True
				self.score = int(score)
				self.feedback_message = message
				db.session.commit()
				return True, 200 #OK
		else:
			return False, 403 #Forbidden




	def __repr__(self):
		return "<booking: %s>" % self.id