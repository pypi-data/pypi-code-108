# This file is part of Sympathy for Data.
# Copyright (c) 2017 Combine Control Systems AB
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
import os
import unittest
import fnmatch
import sys
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(TEST_DIR, '..', '..', 'Test', 'Unit'))
import run_workflow  # noqa


def test_workflows():
    """Test MATLAB workflows"""
    for dirpath, dirnames, filenames in os.walk(TEST_DIR):
        for filename in fnmatch.filter(filenames, '*.syx'):
            yield run_workflow.run_workflow([os.path.join(TEST_DIR, filename)])


if __name__ == '__main__':
    unittest.main()
