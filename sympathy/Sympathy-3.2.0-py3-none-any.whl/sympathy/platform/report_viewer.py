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
import json

import Qt.QtWidgets as QtWidgets
import pygments
import pygments.lexers
import pygments.formatters

from .viewerbase import ViewerBase


class ReportViewer(ViewerBase):
    def __init__(self, report_data=None, console=None, parent=None):
        super().__init__(parent)
        self._report = report_data
        self._report_browser = QtWidgets.QTextBrowser()
        self._report_browser.setFontFamily('courier')

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._report_browser)
        self.setLayout(layout)

        self.update_data(self._report)

    def report(self):
        return self._report

    def data(self):
        return self.report()

    def update_data(self, data):
        if data is not None:
            self._report = data
            obj = json.loads(self.report().get())
            text = json.dumps(obj, indent=2)
            html = pygments.highlight(
                '' if text is None else text,
                pygments.lexers.get_lexer_by_name('json'),
                pygments.formatters.get_formatter_by_name('html', full=True))
            self._report_browser.setHtml(html)
