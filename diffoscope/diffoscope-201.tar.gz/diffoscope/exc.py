#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2016-2017, 2020 Chris Lamb <lamby@debian.org>
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

from .tools import get_tool_name, get_package_provider


class OutputParsingError(Exception):
    def __init__(self, operation, object):
        super().__init__()
        self.operation = operation
        self.object_class = object.__class__


class RequiredToolNotFound(Exception):
    def __init__(self, operation):
        super().__init__()
        self.operation = get_tool_name(operation)

    def get_comment(self, infix=""):
        xs = [
            "'{}' not available in path.".format(self.operation),
            infix,
        ]

        x = get_package_provider(self.operation)
        if x:
            xs.append(
                "Installing the '{}' package may produce a better output.".format(
                    x
                )
            )

        return " ".join(x for x in xs if x)


class ContainerExtractionError(Exception):
    def __init__(self, pathname, wrapped_exc):
        super().__init__()
        self.pathname = pathname
        self.wrapped_exc = wrapped_exc
