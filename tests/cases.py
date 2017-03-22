import unittest
import os
import json

from flask import current_app

from app import create_app, db



class ConfigTestCase(unittest.TestCase):
	"""
	No db is created, we test first if the testing Configuration is used
	to avoide overwritting the development db
	"""
	def setUp(self):
		self.app = create_app('testing')

		self.ctx = self.app.app_context()
		self.ctx.push()

	def tearDown(self):
		self.ctx.pop()



class ViewsTestCase(unittest.TestCase):
	"""
	The test case to use while testing views
	"""
	def setUp(self):
		self.app = create_app('testing')

		self.ctx = self.app.app_context()
		self.ctx.push()

		db.drop_all()
		db.create_all()

		self.client = self.app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
		self.ctx.pop()

	def get(self, url):
		resp = self.client.get(url)

		db.session.remove() #Not using this makes tests hang. A multithreading issue, 
							#Check this: http://docs.sqlalchemy.org/en/latest/orm/contextual.html

		body = resp.get_data(as_text=True)

		if body not in [None, '']:
			try:
				body = json.loads(body)
			except:
				pass

		return body, resp.status_code, resp.headers

	def post(self, url, data, follow_redirects=True):
		resp = self.client.post(url, data=data)
		
		db.session.remove() #Not using this makes tests hang. A multithreading issue, 
							#Check this: http://docs.sqlalchemy.org/en/latest/orm/contextual.html
		body = resp.get_data(as_text=True)

		if body not in [None, '']:
			try:
				body = json.loads(body)
			except:
				pass

		return body, resp.status_code, resp.headers	