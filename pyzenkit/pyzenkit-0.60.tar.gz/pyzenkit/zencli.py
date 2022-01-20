#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Honza Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------
# Notes:
#  - The concept for dynamic module loading was taken from here
#    [1] https://lextoumbourou.com/blog/posts/dynamically-loading-modules-and-classes-in-python/
#-------------------------------------------------------------------------------


"""
.. warning::

    This module is under development, please do not use it yet.

"""


import sys
import pkgutil
import argparse
import logging
import importlib
from pprint import pprint


class ZenCLIModule:
    """
    Base class for all pluggable ZenCLI modules

    All modules must extend this class. Currently there is no base implementation,
    but this can change in the future.
    """
    pass

class ZenCLI:
    """
    Base implementation of simple pluggable command line interface

    This implementation is fully working on its own, however it is recommended to
    customize the functionality via inheritance.
    """
    def __init__(self, **kwargs):
        self.module_domain = kwargs.pop('module_domain', 'zencli_modules')
        self.module_path   = kwargs.pop('module_path',   None)
        self.description   = kwargs.pop('description', 'ZenCLI - Simple generic command line interface')

        self.modules  = {}
        self.commands = {}

        # Setup command line parser
        parser = argparse.ArgumentParser(description = self.description)
        parser.add_argument('-c', '--config-file', help='name of the config file')
        parser.add_argument('-f', '--log-file', help='name of the log file')
        parser.add_argument('-l', '--log', default='warning', help='set logging level')
        parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
        parser.add_argument('command', nargs='?', default='command:list', help='command to be executed')
        parser.add_argument('args', nargs='*', help='optional additional arguments')

        # Load pluggable modules from given path
        self._load_modules(self.module_path, self.module_domain, parser)

        # Register some additional built-in commands
        self.register_command(name='command:list', obj=self, cbk='cbk_command_list', hlp='List all currently available commands')

        # Process command line arguments
        self.arguments = parser.parse_args()

        logging_level = getattr(logging, self.arguments.log.upper(), None)
        if not isinstance(logging_level, int):
            raise ValueError('Invalid log level: %s' % logging_level)
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging_level)

    def __del__(self):
        pass

    def _get_class_name(self, modname):
        """Generate class name from a module file name"""
        output = ""

        # Split on the '_' and ignore the last word 'module'
        #words = modname.split("_")[:-1]
        # Split on the '_'
        words = modname.split("_")
        # Capitalise the first letter of each word and add to string
        for word in words:
            output += word.title()
        return output

    def _load_modules(self, path, domain, parser):
        #logging.info("Loading modules on path '{path}'"\
        #             .format(path=path))
        print("Loading modules on path '{path}'"\
              .format(path=path))

        module_list = pkgutil.iter_modules(path=[path])
        for loader, mod_name, ispkg in module_list:
            # Ensure that module isn't already loaded
            if mod_name not in sys.modules:
                loaded_mod = importlib.import_module(domain + '.' + mod_name)

                # Get the class's name
                class_name = self._get_class_name(mod_name)

                # Load it from imported module
                loaded_class = getattr(loaded_mod, class_name)

                # Create an instance of it
                instance = loaded_class()

                self.modules[class_name] = instance

                print("Found class '{class_name}' within module '{mod_name}' on path '{path}'"\
                      .format(class_name=class_name,mod_name=mod_name,path=path))

        for n, m in self.modules.items():
            print("Registering module {mod_name}"\
                  .format(mod_name=n))
            m.register(self, parser)


    def register_command(self, name, obj, cbk, hlp):
        """Generate class name from a module file name"""
        self.commands[name] = {'obj': obj, 'cbk': cbk, 'hlp': hlp}

    def process(self):
        c = self.arguments.command
        if c in self.commands:
            cobj = self.commands[c]
            cbk = getattr(cobj['obj'], cobj['cbk'])
            cbk(self, self.arguments.args)
        else:
            print("Unknown command '%s'" % c)
            self.cbk_command_list(self, self.arguments.args)

    def cbk_command_list(self, context, args):
        """Generate class name from a module file name"""
        for n,c in sorted(self.commands.items()):
            print("{cmd_name} - {cmd_hlp}".format(cmd_name = n, cmd_hlp = c['hlp']))

if __name__ == "__main__":
    cli = ZenCLI(module_path='./zencli_modules')
    pprint (vars(cli))
    cli.process()
