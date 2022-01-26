# pylint: disable=W1202
"""
Namespace for ExoEdge commands.

"""

import sys
import logging
import importlib
import pkg_resources
import docopt
from exoedge import logger

LOG = logger.getLogger(__name__)


class Command(object):
    """
        Base class for ExoEdge commands.
    """
    Name = 'go'
    def __init__(self, command_args, global_args):
        """
        Initialize the commands.
        :param command_args: arguments of the command
        :param global_args: arguments of the program
        """
        self.args = docopt.docopt(self.__doc__, argv=command_args, options_first=True)
        global_args.update({k:v for k, v in self.args.items() if v})
        self.global_args = global_args

        if isinstance(self.global_args.get('--debug'), str):
            LOG.critical("Setting Level: {}".format(self.global_args.get('--debug')))
            LOG.setLevel(getattr(logging, self.global_args.get('--debug').upper()))

