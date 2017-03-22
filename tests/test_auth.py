from cases import ViewsTestCase, db

from flask import url_for

from flask_login import current_user

from app.models import User

import logging

import os 

dir_path = os.path.dirname(os.path.realpath(__file__))

print dir_path

logging.basicConfig(filename=dir_path+'/test.log', level=logging.DEBUG, filemode='w')


class AuthViewsTest(ViewsTestCase):
	"""
	"""
	def test_authGET(self):
		#The choice view
		body, status_code, headers = self.get(url_for('auth.registration_choice'))
		_ = (status_code == 200)
		self.assertTrue(_)

		#The connexion - GET
		body, status_code, headers = self.get(url_for('auth.login'))
		_ = (status_code == 200)
		self.assertTrue(_)
		
		#The client registration - GET
		body, status_code, headers = self.get(url_for('auth.register_client'))
		_ = (status_code == 200)
		self.assertTrue(_)

		#The prof registration - GET
		body, status_code, headers = self.get(url_for('auth.register_prof'))
		_ = (status_code == 200)
		self.assertTrue(_)

		body, status_code, headers = self.get(url_for('auth.unconfirmed'))
		_ = (status_code == 302) #Anonymous user, expected redirection
		self.assertTrue(_)

		body, status_code, headers = self.get(url_for('auth.resend_confirmation'))
		_ = (status_code == 302) 
		self.assertTrue(_)

	def register_client(self, email, first_name, last_name, username, password=123,
						password_confirmation=123):
		data = {
		'email': email,
		'password': password,
		'password_confirmation': password_confirmation,
		'first_name': first_name,
		'last_name' : last_name,
		'username': username
		}

		body, status_code, headers = self.post(url_for('auth.register_client'), data=data)

		return body, status_code, headers

	def register_prof(self, email, first_name, last_name, username, password=123,
						password_confirmation=123):
		data = {
		'email': email,
		'password': password,
		'password_confirmation': password_confirmation,
		'first_name': first_name,
		'last_name' : last_name,
		'username': username
		}

		body, status_code, headers = self.post(url_for('auth.register_prof'), data=data)

		return body, status_code, headers


	def test_registration(self):
		#registering a client
		self.register_client('client1@bar.com', 'client', 'testy', 'client1')
		self.assertTrue(User.query.filter_by(username = 'client1').all())

		#Registering a client with same email
		self.register_client('client1@bar.com', 'clien', 'test', 'client2')
		self.assertFalse(User.query.filter_by(username = 'client2').all())

		#Registering a client, but made a mistake on password verification
		self.register_client('foo@baaaar.com', 'client', 'testy', 'client2',
							  '123', 'abc')
		self.assertFalse(User.query.filter_by(username = 'client2').all())



		#registering a prof
		self.register_client('prof1@foobar.com', 'prof', 'testy', 'prof1')
		self.assertTrue(User.query.filter_by(username = 'prof1').all())

	def test_login_logout(self):
		self.register_client('client1@bar.com', 'client', 'testy', 'client1')
		client = User.query.filter_by(username = 'client1').first()

		data = {
			'email'   : 'client1@bar.com',
			'password': '123'
		}

		#Creating a context request to check if the user is logged in
		with self.client:
			body, status_code, headers = self.post(url_for('auth.login'), data=data)
			self.assertTrue(status_code == 302)

			self.assertTrue(headers['Location'] == url_for('main.index', _external=True))

			self.assertTrue(client == current_user)

			self.assertFalse(client.confirmed)

			#lets confirm the user
			body, status_code, headers = self.get(url_for('auth.resend_confirmation'))
			token = body

			body, status_code, headers = self.get(url_for('auth.confirm', token=token))
			logging.debug(body)

		with self.client:
			#login
			body, status_code, headers = self.post(url_for('auth.login') , data=data)

			self.assertTrue(current_user.email == data['email'])
			self.assertTrue(current_user.confirmed)

			#Logout
			body, status_code, headers = self.get(url_for('auth.logout'))
			self.assertTrue(current_user.is_anonymous())

		with self.client:
			#register profs and vlients, make some bookings and test booking actions
