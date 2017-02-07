from app import create_app, db
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand

from app.models import Role

#The manager from flask_script can take a factory function as an argument,
# the manager method run() creats an app and runs it
#No need to create an app like this:
#app = create_app('default')

manager = Manager(create_app)

def shell_context_maker():
	return dict(db=db, Role=Role)

manager.add_command("shell", Shell(make_context = shell_context_maker))
manager.add_command("db", MigrateCommand)

@manager.command
def createdb(drop_first=False):
	"""Creates the database"""
	if drop_first:
		db.drop_all()
	db.create_all()

if __name__ == '__main__':

	manager.run()