import os

PROJECT_DB_PASSWORD = os.environ.get('POSTGRES_DB_PASSWORD')	

class Config(object):
	DEBUG = False
	TESTING = False
	SECRET_KEY = "8734tg374z3huo53u80hr808w"

	# The email of the administrator
	APP_ADMIN = os.environ.get('APP_ADMIN') or 'med.tiour@gmail.com' 

	APP_MAIL_SUBJECT_PREFIX = '[Compagnon]'
	APP_MAIL_SENDER         = 'Compagnon Admin <freelancer.arjjuna@gmail.com>'


	#Getting a warning from SQLAlchemy to set this variable value to True
	SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
	DEBUG = True

	MAIL_SERVER             = 'smtp.gmail.com'
	MAIL_PORT               = 587
	MAIL_USE_TLS            = True
	MAIL_USERNAME           = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD           = os.environ.get('MAIL_PASSWORD')

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/dev_db_1'

class TestingConfig(Config):
	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/test_db_1'


config = {
	"development": DevelopmentConfig,
	"testing"    : TestingConfig,
	"default"    : DevelopmentConfig
}