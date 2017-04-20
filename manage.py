# -*- coding: utf-8 -*-
import os
import subprocess
import sys


import eventlet
eventlet.monkey_patch()

from app import create_app, db, socketio

from app import utils as uts

from flask_script import Manager, Command, Shell, Server as _Server, Option
from flask_migrate import MigrateCommand

from app.models import Role, User, Prof, Client, Message, Subject, Level, Education, \
						Experience, City, Notification, ChatStatus


#The manager from flask_script can take a factory function as an argument,
# the manager method run() creats an app and runs it
#No need to create an app like this:
#app = create_app('default')

manager = Manager(create_app)

class Server(_Server):
	help = description = 'Runs the Socket.IO web server'

	def get_options(self):
		options = (
			Option('-h', '--host',
					 dest='host',
					 default=self.host),

			Option('-p', '--port',
					 dest='port',
					 type=int,
					 default=self.port),

			Option('-d', '--debug',
					 action='store_true',
					 dest='use_debugger',
					 help=('enable the Werkzeug debugger (DO NOT use in '
						 'production code)'),
					 default=self.use_debugger),
			Option('-D', '--no-debug',
					 action='store_false',
					 dest='use_debugger',
					 help='disable the Werkzeug debugger',
					 default=self.use_debugger),

			Option('-r', '--reload',
					 action='store_true',
					 dest='use_reloader',
					 help=('monitor Python files for changes (not 100%% safe '
						 'for production use)'),
					 default=self.use_reloader),
			Option('-R', '--no-reload',
					 action='store_false',
					 dest='use_reloader',
					 help='do not monitor Python files for changes',
					 default=self.use_reloader),
		)
		return options

	def __call__(self, app, host, port, use_debugger, use_reloader):
		# override the default runserver command to start a Socket.IO server
		if use_debugger is None:
			use_debugger = app.debug
			if use_debugger is None:
				use_debugger = True
		if use_reloader is None:
			use_reloader = app.debug
		socketio.run(app,
					 host=host,
					 port=port,
					 debug=use_debugger,
					 use_reloader=use_reloader,
					**self.server_options)


default_config = os.environ.get('FLASK_CONFIG') or "default"

manager.add_command("runserver", Server())
manager.add_option('-c', '--config', dest='config_name', required=False, default=default_config)
manager.add_command("db", MigrateCommand)


def shell_context_maker():
	return dict(uts=uts, db=db, Role=Role, User=User, Prof=Prof, Client=Client, Message=Message,
				Subject=Subject, Education=Education, Experience=Experience, City=City,
				Notification=Notification, ChatStatus=ChatStatus, Level=Level)

manager.add_command("shell", Shell(make_context = shell_context_maker)) 


@manager.command
def createdb(drop_first=False):
	"""Creates the database"""
	if drop_first:
		db.drop_all()
	db.create_all()


class CeleryWorker(Command):
	"""Starts the celery worker."""
	name = 'celery'
	capture_all_args = True

	def run(self, argv):
		ret = subprocess.call(
			['celery', 'worker', '-A', 'app.celery'] + argv)
		sys.exit(ret)

class GunicornServer(Command):
	"""Starts the celery worker."""
	name = 'grunserver'
	capture_all_args = True

	def run(self, argv):
		ret = subprocess.call(
		['gunicorn', '--worker-class', 'eventlet', '-w', '3', '--bind',
		 '0.0.0.0:5000', 'app.wsgi:app'] + argv)

		sys.exit(ret)





@manager.command
def test():
	"""runs unittesting"""
	tests = subprocess.call(['python', '-c', 'import tests;' 'tests.run()'])
	sys.exit(tests)

manager.add_command("celery", CeleryWorker())
manager.add_command("grunserver", GunicornServer())

if __name__ == '__main__':
	if sys.argv[1] == 'test':
		os.environ['FLACK_CONFIG'] = 'testing'

	manager.run()