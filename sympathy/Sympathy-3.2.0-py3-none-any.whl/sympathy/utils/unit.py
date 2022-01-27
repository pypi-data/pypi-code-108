# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
from nose.plugins.skip import SkipTest


def skip(function):
    """
    Decorator for skipping test when run by nosetests.
    Skipped tests will not count towards successes or failures.
    """
    def skipped(*args, **kwargs):
        raise SkipTest('Skipping {0}'.format(function.__name__))
    skipped.__name__ = function.__name__
    return skipped
