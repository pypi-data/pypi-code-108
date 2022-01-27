# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
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
import sys
from Qt import QtWidgets, QtCore
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtGui import QOpenGLContext


class WebPage(QtWidgets.QWidget):
    finished = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        view = QWebEngineView(parent=self)
        layout.addWidget(view)
        self.setLayout(layout)
        policy = self.sizePolicy()
        policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
        policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        self.setSizePolicy(policy)
        self.view = view

        view.urlChanged.connect(self._view_url_changed)
        view.loadStarted.connect(self._view_load_started)
        print('Created with OpenGL:', QOpenGLContext.openGLModuleType())

    def _view_url_changed(self, url):
        print('URL changed to', url.toString())

    def _view_load_started(self):
        print('Load started')


def main():
    QtWidgets.QApplication.setAttribute(
        QtCore.Qt.AA_ShareOpenGLContexts, True)
    if sys.platform == 'win32':
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseOpenGLES, True)
    app = QtWidgets.QApplication(sys.argv)
    page = WebPage()
    page.setMinimumHeight(600)
    page.setMinimumWidth(800)
    address = 'https://www.sympathyfordata.com'
    page.view.load(address)
    page.show()
    app.exec_()


if __name__ == '__main__':
    main()
