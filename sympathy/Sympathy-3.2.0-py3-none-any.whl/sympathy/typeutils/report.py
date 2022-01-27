# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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

from sympathy.utils import filebase
from sympathy.utils import port
from .. utils.context import inherit_doc


def is_report(scheme, filename):
    return File.is_type(filename, scheme)


def is_reports(scheme, filename):
    return FileList.is_type(filename, scheme)


@filebase.typeutil('sytypealias report = sytext')
@inherit_doc
class File(filebase.TypeAlias):
    """Report type."""

    def set(self, report_data):
        self._data.set(report_data)

    def get(self):
        # If data is not set return an empty (json-encoded) dictionary instead
        # of empty string so the result can always be json decoded.
        return self._data.get() or '{}'

    def update(self, other):
        self._data.update(other._data)

    def source(self, other, shallow=False):
        self.set(other.get())

    @classmethod
    def viewer(cls):
        from .. platform import report_viewer
        return report_viewer.ReportViewer

    @classmethod
    def icon(cls):
        return 'ports/report.svg'


@inherit_doc
class FileList(filebase.FileListBase):
    """List of reports type."""

    sytype = '[report]'
    scheme = 'text'


def Report(description, name=None):
    return port.PortType(description, 'report', scheme='text', name=name)


def Reports(description, name=None):
    return port.PortType(description, '[report]', scheme='text', name=name)
