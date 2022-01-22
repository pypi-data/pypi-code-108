from fava.core.server import console
from fava.core.utils import helper
from fava.core.http import route, controller
from fava.core.database import migration, model


def run_server(server):
    """
    Run development server
    """
    return console.run(server)


def create_migration(name):
    """
    Create new migration file
    :param name:
    """
    return migration.create_new_migration(name)


def migrate(name):
    """
    Run database migrate
    :param name: str
    """
    return migration.run_migrate(name)


def create_model(name):
    """
    Create database model file
    """
    return model.create_new_model(name)


def create_controller(name):
    """
    Create new controller file
    """
    return controller.create_new_controller(name)


def create_route(name):
    """
    Create new route file
    """
    return route.create_new_route(name)


def generate_secret_key():
    """
    Generate new Secret Key
    """
    return helper.generate_secret_key()
