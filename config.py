import os

PROJECT_DB_PASSWORD = os.environ.get('POSTGRES_DB_PASSWORD') or ""

class Config(object):
	DEBUG = False
	TESTING = False
	SECRET_KEY = "8734tg374z3huo53u80hr808w"

	# The email of the administrator
	APP_ADMIN = os.environ.get('APP_ADMIN') or 'med.tiour@gmail.com' 

	APP_MAIL_SUBJECT_PREFIX = '[OStudy]'
	APP_MAIL_SENDER         = 'Ostudy Admin <freelancer.arjjuna@gmail.com>'


	ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


	#Getting a warning from SQLAlchemy to set this variable value to True
	SQLALCHEMY_TRACK_MODIFICATIONS = True

	MAX_CONTENT_LENGTH = 16 * 1024 * 1024

	LONG_POLL_SLEEP = 2

class DevelopmentConfig(Config):
	DEBUG = True

	APP_UPLOAD_FOLDER   =  '/home/arjjuna/flask/compagnon/compagnon/app/static/uploads'
	USERS_UPLOAD_FOLDER =  '/home/arjjuna/flask/compagnon/compagnon/app/static/uploads/users'
	USERS_UPLOAD_FOLDER_RELATIVE =  'uploads/users'
	APP_STATIC_FOLDER   = '/home/arjjuna/flask/compagnon/compagnon/app/static'
	

	MAIL_SERVER             = 'smtp.gmail.com'
	MAIL_PORT               = 587
	MAIL_USE_TLS            = True
	MAIL_USERNAME           = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD           = os.environ.get('MAIL_PASSWORD')

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/dev_db_1'

	CELERY_CONFIG = {}


class TestingConfig(Config):
	TESTING = True

	WTF_CSRF_ENABLED = False

	SERVER_NAME = '127.0.0.1:5000'

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/test_db_1'

	CELERY_CONFIG = {'CELERY_ALWAYS_EAGER': True}

class ProductionConfig(Config):
	DEBUG = False
	CELERY_CONFIG = {}

	SERVER_NAME = '207.154.228.229'

	APP_UPLOAD_FOLDER   =  '/home/arjjuna/compagnon/app/app/static/uploads'
	USERS_UPLOAD_FOLDER =  '/home/arjjuna/compagnon/app/app/static/uploads/users'
	USERS_UPLOAD_FOLDER_RELATIVE =  'uploads/users'
	APP_STATIC_FOLDER   = '/home/arjjuna/compagnon/app/app/static'

	MAIL_SERVER             = 'smtp.gmail.com'
	MAIL_PORT               = 587
	MAIL_USE_TLS            = True
	MAIL_USERNAME           = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD           = os.environ.get('MAIL_PASSWORD')

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/ostudy'

config = {
	"development": DevelopmentConfig,
	"testing"    : TestingConfig,
	"production" : ProductionConfig,
	"default"    : DevelopmentConfig
}
