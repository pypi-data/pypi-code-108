# This file is part of Sympathy for Data.
# Copyright (c) 2018, Combine Control Systems AB
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
from collections import OrderedDict


class ErrorHandling(object):

    def fail(self, error):
        raise error

    @property
    def is_error(self):
        return False


_basic_error_options = OrderedDict([
    ('error', 'Error'),
    ('empty', 'Create Empty Item')])

_basic_list_error_options = OrderedDict([
    ('error', 'Error'),
    ('empty', 'Create Empty Item'),
    ('skip', 'Skip Item')])


_error_names = ['error', 'exception', 'fail']


class BasicErrorHandling(ErrorHandling):

    def __init__(self, options, key_or_index):
        self._options = options

        if self._options.get(key_or_index) is not None:
            self._key = key_or_index
        else:
            self._key = list(self._options.keys())[key_or_index]

    def keys(self):
        return self._options.keys()

    def descriptions(self):
        return self._options.values()

    @property
    def is_error(self):
        if self._key.lower() in _error_names:
            return True


class ErrorStrategy(object):
    def __init__(self, options, handling_factory):
        self._options = options
        self._handling = handling_factory

    def keys(self):
        return self._options.keys()

    @property
    def descriptions(self):
        return self._options.values()

    @property
    def options(self):
        return self._options

    def is_error(self, key_or_index):
        return self._handling(
            self._options, key_or_index).is_error


_strategies = {
    'basic': ErrorStrategy(
        _basic_error_options,
        BasicErrorHandling),
    'basic_list': ErrorStrategy(
        _basic_list_error_options,
        BasicErrorHandling)
}


def strategy(name):
    return _strategies[name]
