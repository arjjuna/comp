from . import db, login_manager

from datetime import datetime

from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class Permission:
	"""A binary representation of permissions.
	Can sum two permissions (example: 0b001+0b100 = 0b101)"""
	EDIT_SELF =   0b000001
	ADMINISTER  = 0b100000

class Role(db.Model):
	"""Users roles, simple user or admin (not to confuse with Client, Prof)"""
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(64), unique=True)
	default = db.Column(db.Boolean, default=False)
	permissions = db.Column(db.Integer)

	users = db.relationship('User', backref='role')

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

class User(UserMixin, db.Model):
	"""User model"""
	__tablename__ = 'users'
	id            = db.Column(db.Integer, primary_key=True)
	email         = db.Column(db.String(64), unique=True)
	password_hash = db.Column(db.String(128))
	first_name    = db.Column(db.String(64))
	last_name     = db.Column(db.String(64))
	picture       = db.Column(db.String(500))
	member_since  = db.Column(db.DateTime(), default=datetime.utcnow)
	confirmed     = db.Column(db.Boolean, default=False)
	last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
	
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
	
	
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
	
	def __init__(self, **kwargs):
		super(User, self).__init__(**kwargs)
		if self.role is None:
			if self.email == current_app.config['APP_ADMIN']:
				self.role = Role.query.filter_by(name='administrator').first()
			if self.role is None:
				self.role = Role.query.filter_by(name='user').first()
			if self.picture is None:
				self.picture = current_app.config['APP_UPLOAD_FOLDER'] + '/' + "150x150_placeholder.png"
	
	def __repr__(self):
		return '<User %r, email: %r>' % (self.username, self.email)
		
class AnonymousUser(AnonymousUserMixin):
	# Anonymous user, requirement of the Flask-login extension
	def can(self, permission):
		return false
	def is_administrator(self, permission):
		return false

@login_manager.user_loader
def load_user(user_id):
	# User loader, requirement of the Flask-login extension
	return User.query.get(int(user_id))

class Message(db.Model):
	__tablename__ = 'messages'
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(250))
	timestamp = db.Column(db.DateTime(), default=datetime.utcnow)

	from_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	to_id = db.Column(db.Integer, db.ForeignKey('users.id'))

