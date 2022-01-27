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
import Qt.QtWidgets as QtWidgets


def print_mime(mime):
    text = []
    text.append(', '.join(mime.formats()))
    for format in mime.formats():
        text.append('{}: {}'.format(format, mime.data(format).data()))
    return '\n'.join(text)


class Dropbox(QtWidgets.QTextEdit):
    """This widget is used for debugging drag and drop applications."""

    def __init__(self, parent=None):
        super(Dropbox, self).__init__(parent)
        self.resize(300, 300)
        self.setAcceptDrops(True)
        self.setWindowTitle('Dropbox')

    def dragEnterEvent(self, event):
        self.append('dragenter:\n'
                    'MIME: {}\n'
                    'dropaction: {}\n'.format(print_mime(event.mimeData()),
                                              event.dropAction()))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    dropbox = Dropbox()
    dropbox.show()
    app.exec_()
