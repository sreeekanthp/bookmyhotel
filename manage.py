from flask.ext.script import Manager, Command, Option
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script.commands import InvalidCommand
from models import application, db, User


class CreateSuperUser(Command):
    """ Create a superuser with admin privileges. """

    def __init__(self, default_username='admin', default_password='password'):
        self.default_username = default_username
        self.default_password = default_password

    def get_options(self):
        return [
            Option('-u', '--username', dest='username', default=self.default_username),
            Option('-p', '--password', dest='password', default=self.default_password),
        ]

    def run(self, username, password):
        if User.query.filter_by(username=username).first() is not None:
            raise InvalidCommand("User with this username already exists")

        user = User(username, username.title(), password, True)
        user.add(user)
        print ("Superuser `%s` created successfully" % username)

migrate = Migrate(application, db)
manager = Manager(application)
manager.add_command('create_superuser', CreateSuperUser())
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
