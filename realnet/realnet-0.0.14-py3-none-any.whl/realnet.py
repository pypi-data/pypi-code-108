from pynecone import Shell

from .account import Account
from .app import App
from .item import Item
from .type import Type
from .function import Function
from .topic import Topic
from .acl import Acl
from .tenant import Tenant
from .auth import Auth
from .group import Group
from .worker import Worker

class Realnet(Shell):

        def __init__(self):
            super().__init__('realnet')

        def get_commands(self):
            return [
                    Item(),
                    Type(),
                    Worker(),
                    Function(),
                    Topic(),
                    Acl(),
                    Tenant(),
                    Auth(),
                    Group(),
                    Account(),
                    App()
            ]

        def add_arguments(self, parser):
            pass

        def get_help(self):
            return 'Realnet shell'