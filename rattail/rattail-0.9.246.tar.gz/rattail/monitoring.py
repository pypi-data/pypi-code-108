# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Monitoring Library

This contains misc. common/shared logic for use with multiple types of
monitors, e.g. datasync, filemon etc.
"""

from __future__ import unicode_literals, absolute_import

import os
import logging
import subprocess

from rattail.config import parse_bool, parse_list


log = logging.getLogger(__name__)


class MonitorAction(object):
    """
    Base class for monitor actions.  Note that not all actions are
    class-based, but the ones which are should probably inherit from
    this class.
    """

    def __init__(self, config):
        self.config = config
        self.app = config.get_app()
        self.enum = config.get_enum()
        self.model = config.get_model()

    def __call__(self, *args, **kwargs):
        """
        This method must be implemented in the subclass; it defines
        what the action actually *does*.  The monitor daemon will
        invoke this method for all new items which are discovered.
        """
        raise NotImplementedError


class CommandAction(MonitorAction):
    """
    Simple action which can execute an arbitrary command, as a
    subprocess.  This action is meant to be invoked with a particular
    file path, which is to be acted upon.
    """

    def __init__(self, config, cmd):
        super(CommandAction, self).__init__(config)
        self.cmd = cmd

    def __call__(self, path, **kwargs):
        """
        Run the command for the given file path.
        """
        filename = os.path.basename(path)
        shell = parse_bool(kwargs.pop('shell', False))

        if shell:
            # TODO: probably shoudn't use format() b/c who knows what is in
            # that command line, that might trigger errors
            cmd = self.cmd.format(path=path, filename=filename)

        else:
            cmd = []
            for term in parse_list(self.cmd):
                term = term.replace('{path}', path)
                term = term.replace('{filename}', filename)
                cmd.append(term)

        log.debug("final command to run is: %s", cmd)
        subprocess.check_call(cmd, shell=shell)
