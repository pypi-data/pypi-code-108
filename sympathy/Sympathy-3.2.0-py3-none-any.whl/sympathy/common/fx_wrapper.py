# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
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
"""
This module contains classes that wrap tables or lists of tables for use in
various function selector, F(x), nodes in Sympathy for Data.
"""
import sys
from sympathy.platform import exceptions as syexceptions
from sympathy.utils.context import deprecated_warn


class Fx(object):
    """
    Fx should be used as the parent class for classes to be used
    in the generic F(x) nodes.

    execute is the method with will be called and it can be regarded as the
    function wrapped.
    arg_types is a list with string types as shown in port tooltips
    and it determines the types of data that the function is compatible with.

    When subclassing and creating your own function make sure to override both
    arg_types and execute.
    """
    arg_types = ['<a>']
    list_wrapper = False

    def __init__(self, arg, res, extra_arg=None):
        self.res = res
        self.arg = arg
        # Extra arg is never used.
        self.extra_arg = None
        if self.list_wrapper:
            deprecated_warn('Using list_wrapper = True '
                            'is no longer supported and has no useful effect')

    def execute(self):
        """
        Execute is called from F(x) or F(x) List nodes.

        Access input and output data using self.res and self.arg respectively.
        Override this function to provide a useful behavior.
        """
        raise syexceptions.SyConfigurationError(
            "This f(x) script doesn't implement an execute method.")


class FxWrapper(Fx):
    pass


class FxArg(Fx):

    def __init__(self, arg, res, extra_arg=None):
        super().__init__(arg, res, extra_arg=extra_arg)

    def execute(self):
        try:
            self.function(self.arg, self.res)
        except Exception:
            raise syexceptions.SyUserCodeError(
                sys.exc_info(),
                'Error evaluating function, see underlying cause.')


def decorator(arg_types):
    def inner(func):
        return type(f'Fx_{func.__name__}_cls', (FxArg,), {
            'arg_types': arg_types,
            'list_wrapper': False,
            'function': lambda self, arg, res: func(arg, res)})
    return inner
