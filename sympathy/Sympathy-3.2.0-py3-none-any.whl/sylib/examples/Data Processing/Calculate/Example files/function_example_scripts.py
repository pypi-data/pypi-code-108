# This file is part of Sympathy for Data.
# Copyright (c) 2017, Combine Control Systems AB
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
from sympathy.api import fx_wrapper


class FxList(fx_wrapper.FxWrapper):
    """Apply function to each element in arg separately.
    Element is accessed as in_element = arg
    """

    arg_types = ['<a>']

    def execute(self):
        # See the API description in the Help (under Data type
        # APIs) for more information on how to write functions.

        # This example copies the input to output
        in_element = self.arg
        self.res.source(in_element)


class Fx(fx_wrapper.FxWrapper):
    """Apply function to the whole input.
    Elements are accessed as in_element = arg[index]
    """

    arg_types = ['[<a>]']

    def execute(self):
        # See the API description in the Help (under Data type
        # APIs) for more information on how to write functions.

        # This example copies the first element to output
        in_element = self.arg[0]
        self.res.append(in_element)
