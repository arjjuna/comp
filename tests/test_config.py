from flask import current_app
from config import TestingConfig

from cases import ConfigTestCase

class ConfigTest(ConfigTestCase):
	def test_configuration(self):
		_ = current_app.config['SQLALCHEMY_DATABASE_URI'] == \
			self.app.config['SQLALCHEMY_DATABASE_URI'] == \
			TestingConfig.SQLALCHEMY_DATABASE_URI

		self.assertTrue(_)