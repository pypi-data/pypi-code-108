import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import subprocess
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


class _Brightness(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_Brightness, self).__init__(parent)


        loadUi(os.path.join(currentdir,'brightness.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)

    def closeEvent(self,event):
        print("_Brightness is closing")

    def config(self):
        try:
            self.slider.setMaximum(10)
            self.slider.setValue(8)
            subprocess.call(['sudo /home/pi/set_backlight.dat',str(8)],shell=True)
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.slider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.slider.valueChanged.connect(self.slider_hook)
            pass
        except Exception as error:
            print(error)

    def slider_hook(self, value):
        try:
            cmd ='sudo /home/pi/set_backlight.dat '+str(value)
            print(cmd)
            subprocess.call([cmd],shell=True)
            print(value)
            pass
        except Exception as error:
            print(error)
if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    window=_Brightness()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
