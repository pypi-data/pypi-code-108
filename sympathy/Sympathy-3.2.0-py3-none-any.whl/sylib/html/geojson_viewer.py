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

from PySide2 import QtWidgets, QtCore
from PySide2.QtWebEngineWidgets import QWebEngineView

from sympathy.api.typeutil import ViewerBase
from sympathy.utils.prim import localuri

from sylib.html.webengine import GeoJSONWebPageView


class GeoJSONWidget(QtWidgets.QWidget):
    def __init__(self, json_dict, parent=None):
        super().__init__(parent)
        self.json_dict = json_dict

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

    def _init_gui(self):
        self.preview = QWebEngineView()
        self.preview_page = GeoJSONWebPageView()
        self.preview_page.data = self.json_dict
        self.preview_page.profile().clearHttpCache()
        self.preview.setPage(self.preview_page)

        self.error_textedit = QtWidgets.QTextEdit()

        leaflet_html_filepath = os.path.join(
            os.path.dirname(__file__), 'leaflet', 'index.html')

        #print(leaflet_html_filepath)

        self.preview.setUrl(QtCore.QUrl(localuri(leaflet_html_filepath)))
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


class GeoJSONViewer(ViewerBase):
    def __init__(self, data=None, console=None, parent=None):
        super().__init__(parent)
        self._data = data

        self.view = GeoJSONWidget(self._data.get())
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.view)

        self.setLayout(layout)

    def data(self):
        return self._data

    def update_data(self, data):
        if data is not None:
            self.view.preview_page.data = data.get()
