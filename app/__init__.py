import os

from flask import Flask
from config import config

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_socketio import SocketIO
from celery import Celery

import locale
locale.setlocale(locale.LC_TIME, 'fr_FR')


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
mail = Mail()
socketio = SocketIO()
celery = Celery(__name__, broker="amqp://localhost", backend="rpc://localhost")


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


# Import models so they are visible to SQLAlchemyy
# (the models module imports db from the current package,
# thats why the models import is done after the instanciation of db)
from . import models
from . import sockets
from . import tasks

DEFAULT_CONFIG = os.environ.get('FLASK_CONFIG') or "default"

def create_app(config_name=DEFAULT_CONFIG):
	app = Flask(__name__)
	app.config.from_object(config[config_name])

	db.init_app(app)
	migrate.init_app(app, db)
	login_manager.init_app(app)
	bootstrap.init_app(app)
	mail.init_app(app)
	socketio.init_app(app)

	celery.conf.update(config[config_name].CELERY_CONFIG)

	#Main blueprint, public urls
	from main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	#Authentication blueprint
	from auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint, url_prefix="/auth")

	#Client blueprint
	from client import client as client_blueprint
	app.register_blueprint(client_blueprint, url_prefix="/client")

	#Prof blueprint
	from prof import prof as prof_blueprint
	app.register_blueprint(prof_blueprint, url_prefix="/prof")

	#My Blueprint, for testing purposes
	from mybp import mybp as my_blueprint
	app.register_blueprint(my_blueprint, url_prefix="/test")

	return app