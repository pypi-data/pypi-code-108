# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
import tempfile as _tempfile
import os


def tempdir():
    dirname = os.path.join(_tempfile.gettempdir(), 'sympathy')
    os.makedirs(dirname, exist_ok=True)
    return dirname


def tempfile(suffix=None, prefix=None):
    fileno, filename = _tempfile.mkstemp(suffix=suffix, prefix=prefix, dir=tempdir())
    os.close(fileno)
    return filename
