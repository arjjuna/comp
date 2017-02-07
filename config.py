import os

PROJECT_DB_PASSWORD = os.environ.get('POSTGRES_DB_PASSWORD')	

class Config(object):
	DEBUG = False
	TESTING = False
	SECRET_KEY = "8734tg374z3huo53u80hr808w"

	#Getting a warning from SQLAlchemy to set this variable value to True
	SQLALCHEMY_TRACK_MODIFICATIONS = True

class DevelopmentConfig(Config):
	DEBUG = True

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/dev_db_1'

class TestingConfig(Config):
	TESTING = True

	SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:' + PROJECT_DB_PASSWORD + '@localhost/test_db_1'


config = {
	"development": DevelopmentConfig,
	"testing"    : TestingConfig,
	"default"    : DevelopmentConfig
}
