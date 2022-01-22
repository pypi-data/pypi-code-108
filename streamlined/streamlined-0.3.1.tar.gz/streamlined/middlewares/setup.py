from .action import Action
from .middleware import Context


class Setup(Action):
    pass


SETUP = Setup.get_name()
