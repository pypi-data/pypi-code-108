#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2020 Chris Lamb <lamby@debian.org>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import abc
import logging

logger = logging.getLogger(__name__)


class Operation(metaclass=abc.ABCMeta):
    def __init__(self, path):
        self.path = path
        self.returncode = None
        self.error_string = None

    @abc.abstractmethod
    def start(self):
        raise NotImplementedError()

    @abc.abstractproperty
    def name(self):
        """
        Name of the operation, e.g. "readelf" or "objdump"
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def full_name(self, truncate=None):
        """
        Full name of the operation, that will be used to call
        command_excluded, e.g. "readelf --debug-dump=info"
        """
        raise NotImplementedError()

    def filter(self, line):
        # Assume operation output is utf-8 by default
        return line

    def terminate(self):
        pass

    def should_show_error(self):
        """
        Whether or not the operation resulted in an unexpected error which
        should be displayed rather than output
        """
        return False

    @abc.abstractproperty
    def output(self):
        raise NotImplementedError()
