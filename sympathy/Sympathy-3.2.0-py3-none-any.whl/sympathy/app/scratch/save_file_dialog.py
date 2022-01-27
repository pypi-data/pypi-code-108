# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import Qt.QtCore as QtCore


def save():
    default_filename = 'save_file_dialog.py'

    # # Result: Shows a native dialog in Gnome, but with the same bug! Native
    # # dialog doesn't ask if I am sure that I want to overwrite file 'example'
    # # since it doesn't exist, then Qt returns filename 'example.py'.
    # dialog = QtWidgets.QFileDialog(
    #     None, "Select file", default_filename,
    #     filter="Python module (*.py)")
    # dialog.setDefaultSuffix('.py')
    # dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
    # dialog.exec_()
    # filename = dialog.selectedFiles()

    # Result: Setting a default_filename with suffix reduces the problem of
    # manually having to type in the extension.
    filename, _ = QtWidgets.QFileDialog.getSaveFileName(
        None, "Select file", default_filename,
        filter="CSV files (*.py)")
    print(filename)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QPushButton("save")
    w.clicked.connect(save)
    w.show()
    app.exec_()
