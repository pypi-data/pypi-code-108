# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
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
import tempfile

from PySide2 import QtWidgets
from PySide2.QtWebEngineWidgets import QWebEngineView

from sympathy.api import qt2 as qt_compat
QtCore = qt_compat.QtCore

from sympathy.api.typeutil import ViewerBase
from sympathy.utils.prim import localuri


def create_html_tempfile():
    fd1, tmp_html = tempfile.mkstemp(
        prefix='report-', suffix='.html')
    os.close(fd1)
    return tmp_html


def write_html_file(rendered_template, tmp_html_path):
    with open(tmp_html_path, 'w', encoding='utf-8') as f:
        f.write(rendered_template)


class HTMLWidget(QtWidgets.QWidget):
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.data = data

        self._init_gui()
        self.center_and_resize(QtWidgets.QApplication.instance())

    def center_and_resize(self, qapp):
        available_size = qapp.desktop().availableGeometry().size()
        width = available_size.width()
        height = available_size.height()
        new_size = QtCore.QSize(width*0.8, height*0.9)

        style = QtWidgets.QStyle.alignedRect(
            QtCore.Qt.LeftToRight,
            QtCore.Qt.AlignCenter,
            new_size,
            qapp.desktop().availableGeometry()
        )
        self.setGeometry(style)

    def write_html(self, html_text):
        write_html_file(html_text, self.tmp_html_path)

        self.preview.setUrl(QtCore.QUrl(localuri(self.tmp_html_path)))

    def _init_gui(self):
        self.preview = QWebEngineView()
        self.preview_page = self.preview.page()

        self.tmp_html_path = create_html_tempfile()

        self.write_html(self.data)
        progressbar = QtWidgets.QProgressBar()
        self.preview_page.loadProgress.connect(progressbar.setValue)

        self.lineedit = QtWidgets.QLineEdit()

        vlayout = QtWidgets.QVBoxLayout()

        policy = QtWidgets.QSizePolicy()
        policy.setHorizontalStretch(0)
        policy.setVerticalStretch(0)
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)

        self.preview.setSizePolicy(policy)
        vlayout.addWidget(self.preview)
        vlayout.addWidget(progressbar)

        self.setLayout(vlayout)


class HtmlViewer(ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super().__init__(parent)
        self._data = data

        self.view = HTMLWidget(data.get())
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.view)

        self.setLayout(layout)

    def data(self):
        return self._data

    def update_data(self, data):
        if data is not None:
            self.view.write_html(data.get())
