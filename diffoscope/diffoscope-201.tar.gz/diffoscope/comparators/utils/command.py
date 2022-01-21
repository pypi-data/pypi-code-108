#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016-2020 Chris Lamb <lamby@debian.org>
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
import signal
import logging
import subprocess

from .operation import Operation
from ...utils import format_cmdline

logger = logging.getLogger(__name__)


class Command(Operation, metaclass=abc.ABCMeta):
    MASK_STDERR = False
    MAX_STDERR_LINES = 25
    VALID_RETURNCODES = {0}

    def start(self):
        logger.debug("Executing %s", self.full_name())

        self._stdin = self.stdin()
        # "stdin" used to be a feeder but we didn't need the functionality so
        # it was simplified into the current form. it can be recovered from git
        # the extra functionality is needed in the future. alternatively,
        # consider using a shell pipeline ("sh -ec $script") to implement what
        # you need, because that involves much less code - like it or not (I
        # don't) shell is still the most readable option for composing processes
        self._process = subprocess.run(
            self.cmdline(),
            close_fds=True,
            env=self.env(),
            input=self.input(),
            stdin=self._stdin,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        self.error_string = self._read_stderr()
        self.returncode = self._process.returncode

    def stdin(self):
        return None

    @abc.abstractmethod
    def cmdline(self):
        raise NotImplementedError()

    @property
    def name(self):
        return self.cmdline()[0]

    def full_name(self, *args, **kwargs):
        kwargs.setdefault("replace", (self.path,))
        return format_cmdline(self.cmdline(), *args, **kwargs)

    def env(self):
        return None  # inherit parent environment by default

    def poll(self):
        pass

    def input(self):
        pass

    def _read_stderr(self):
        if self.MASK_STDERR:
            return ""

        buf = ""
        lines = self._process.stderr.splitlines(True)

        for index, line in enumerate(lines):
            if index >= Command.MAX_STDERR_LINES:
                break
            buf += line.decode("utf-8", errors="replace")

        if len(lines) > Command.MAX_STDERR_LINES:
            buf += "[ truncated after {} lines; {} ignored ]\n".format(
                Command.MAX_STDERR_LINES, len(lines) - Command.MAX_STDERR_LINES
            )

        return buf

    def should_show_error(self):
        # Handle SIGTERM once here as VALID_RETURNCODES may be overriden by
        # subclasses, and we don't want them to have to include it each time
        if self.returncode == -signal.SIGTERM:
            return False

        return self.returncode not in self.VALID_RETURNCODES

    @property
    def output(self):
        return self._process.stdout.splitlines(True)


def our_check_output(cmd, *args, **kwargs):
    logger.debug("Calling external command: %s", " ".join(cmd))

    return subprocess.check_output(cmd, *args, **kwargs)
