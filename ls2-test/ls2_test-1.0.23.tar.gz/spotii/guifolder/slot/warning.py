import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
grandparentdir =  os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)

import title_rc
#from main_paras import mainChannelNotify, getDetectionMode, setOperation
from main_paras import getDetectionMode, setOperation
from define import *


class _Warning(QtWidgets.QWidget):
    def __init__(self,parent=None):
        super(_Warning, self).__init__(parent)

        loadUi(os.path.join(currentdir,'warning.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.resize(96, 224)
        self.slot =0
    def setDetail(self,slot):
        try:
            self.slot=slot+1
            self.number.setText(str(self.slot))
        except Exception as error:
            print(error)
    def buttonHook(self, hookFunction):
        if hookFunction!=None:
            self.button.clicked.connect(hookFunction)
    def config(self):
        try:
            #self.id.lower()
            #self.timer.lower()
            
            pass
        except Exception as error:
            print(error)
            
    def button_click(self):
        try:
            print('slot', self.slot)
            setOperation(self.slot-1, 0)
                
        except Exception as error:
            print(error)


if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    window=_Warning()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
