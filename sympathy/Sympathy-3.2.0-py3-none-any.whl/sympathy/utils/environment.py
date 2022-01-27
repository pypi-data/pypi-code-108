# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import re
from collections import abc
_pattern = re.compile(r'\$\((\w+)(?:=([^\(^\)]+))?\)')


def parse_variables(string):
    return _pattern.finditer(string)


def expand_variables(string: str, variables: abc.Mapping) -> str:
    """
    Expand environment variables matching $(NAME) or $(NAME=DEFAULT).
    """
    matches = parse_variables(string)
    if not matches:
        return string
    diff = 0

    # String as list to allow setitem.
    string_list = list(string)

    for match in matches:
        # Replace according to matched positions.
        name, default = match.groups()
        try:
            value = variables[name]
        except KeyError:
            if default is not None:
                value = default
            else:
                value = f'$({name})'

        start, end = match.span()
        start += diff
        end += diff

        string_list[start:end] = value
        diff += len(value) + start - end

    return ''.join(string_list)


def has_variables(string):
    return next(parse_variables(string), None) is not None
