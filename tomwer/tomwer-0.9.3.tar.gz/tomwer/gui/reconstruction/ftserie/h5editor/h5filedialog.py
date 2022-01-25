# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
############################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "23/02/2017"

from silx.gui import qt
import os


class H5FileDialog(qt.QMessageBox):
    """Class defining the dialog to ask the user an h5 file to be used"""

    defaultH5File = os.path.expanduser("~") + "/.octave/mytomodefaults.h5"

    def __init__(self, parent=None):
        qt.QMessageBox.__init__(self, parent)
        self.setWindowTitle(".h5 file for reconstruction")

        self.h5File = None

        text = "No .h5 found, if you want to process a reconstruction "
        text += "you must give one."
        self.layout().addWidget(qt.QLabel(text), 1, 0)

        if H5FileDialog.hasDefaultH5File():
            buttonText = "Take the default octave file at " + self.defaultH5File
            defaultOctaveFileButton = qt.QPushButton(buttonText)
            defaultOctaveFileButton.setAutoDefault(True)
            defaultOctaveFileButton.clicked.connect(self.__selectDefaultH5File)
            self.layout().addWidget(defaultOctaveFileButton, 1, 0)

        selectFileButtonButton = qt.QPushButton("Select a file")
        self.layout().addWidget(selectFileButtonButton, 2, 0)
        selectFileButtonButton.setAutoDefault(True)

        # rearange the usual QMesageBox buttons
        self.cancelButton = self.addButton(qt.QMessageBox.Cancel)
        self.layout().removeWidget(self.cancelButton)
        self.layout().addWidget(self.cancelButton, 3, 0)
        selectFileButtonButton.clicked.connect(self.__selectFileFromDlg)

    def __selectDefaultH5File(self):
        """
        Set the default h5 file as the selected one
        """
        self.h5File = self.defaultH5File
        self.accept()

    def __selectFileFromDlg(self):
        """
        Launch a QFileDialog to ask the user the path to the h5 file
        """
        self.h5File = H5FileDialog.askForH5File()
        self.accept()

    def exec_(self):
        # If no default h5 file only ask for one.
        if H5FileDialog.hasDefaultH5File():
            qt.QMessageBox.exec_(self)
        else:
            H5FileDialog.askForH5File()

    @staticmethod
    def hasDefaultH5File():
        return os.path.isfile(H5FileDialog.defaultH5File)

    @staticmethod
    def askForH5File(save):
        dialog = qt.QFileDialog()
        title = "Select an h5 file to %s the reconstruction parameters." "" % (
            "save" if save is True else "load"
        )
        dialog.setWindowTitle(title)
        dialog.setModal(1)
        dialog.setNameFilters(["HDF5 file *.h5 *.hdf5"])

        if not dialog.exec_():
            return None

        qapp = qt.QApplication.instance()
        qapp.processEvents()
        return dialog.selectedFiles()[0]
