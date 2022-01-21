import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir)
import title_rc
from cassette_type.cassette_type_wrap import _CassetteTypeDialog
from brightness.brightness import _Brightness
from main_paras import getMainTopLeft
from time_zone.time_zone import _TimeZone


#.QWidget{background-image: url(:/setting/setting_folder/group.png);background-color: transparent;border:0px;}
class _SettingDialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_SettingDialog, self).__init__(parent)


        loadUi(os.path.join(currentdir,'setting.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(93, 124)
        

    def closeEvent(self,event):
        print("Pop dialog is closing")

    def config(self):
        try:
            self.time_zone.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.time_zone.clicked.connect(self.time_zone_hook)
            self.brightness.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.brightness.clicked.connect(self.brightness_hook)
            self.cassette_type.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.cassette_type.clicked.connect(self.cassette_type_hook)
            self.dvp_only.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.dvp_only.clicked.connect(self.dvp_only_hook)
        
            pass
        except Exception as error:
            print(error)

    def dvp_only_hook(self):
        try:
            self.close()
            QtWidgets.qApp.quit()
        except Exception as error:
            print(error)

    def cassette_type_hook(self):
        try:
            popUp = _CassetteTypeDialog()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.exec()
        except Exception as error:
            print(error)

    def brightness_hook(self):
        try:
            popUp = _Brightness()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.exec()
        except Exception as error:
            print(error)

    def time_zone_hook(self):
        try:
            popUp = _TimeZone()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.exec()
            pass
        except Exception as error:
            print(error)

            
    def on_focusChanged(self):
        print('focus changed')

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_SettingDialog()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
