import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)

parentdir = os.path.dirname(currentdir)
grandparentdir =  os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)
g_g_parentdir = os.path.dirname(grandparentdir)
sys.path.insert(0, g_g_parentdir)
import title_rc
from main_paras import mainChannelNotify, getDetectionMode
from define import *


class _CassetteTypeDialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_CassetteTypeDialog, self).__init__(parent)


        loadUi(os.path.join(currentdir,'cassette_type.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)

    def closeEvent(self,event):
        print("Pop dialog is closing")

    def config(self):
        try:
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.chip.clicked.connect(self.chip_selected)
            self.qr.clicked.connect(self.qr_selected)
            if getDetectionMode() == CASSETTE_DETECTION_MODE_AUTO:
                self.chip.setChecked(True)
            else:
                self.qr.setChecked(True)
            pass
        except Exception as error:
            print(error)



    def chip_selected(self):
        try:
            if self.chip.isChecked():
                print('chip checked')
                mainChannelNotify(MAIN_PARA_CASSETTE_TYPE_CHIP)
            else:
                print('chip unchecked')
            pass
        except Exception as error:
            print(error)

    def qr_selected(self):
        try:
            if self.qr.isChecked():
                print('qr checked')
                mainChannelNotify(MAIN_PARA_CASSETTE_TYPE_QR)
            else:
                print('qr unchecked')
            pass
        except Exception as error:
            print(error)

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    window=_CassetteTypeDialog()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
