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
g_g_parentdir = os.path.dirname(grandparentdir)
sys.path.insert(0, g_g_parentdir)

import title_rc
from main_paras import getMainTopLeft
from chg_psw import _ChangePassword
from _language import _Language
import main_paras
from define import *
class _ProfileDetail(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_ProfileDetail, self).__init__(parent)


        loadUi(os.path.join(currentdir,'profile_detail.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        

    def closeEvent(self,event):
        print("_ProfileDetail is closing")

    def config(self):
        try:
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.change_psw.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.change_psw.clicked.connect(self.change_psw_hook)
            self.language.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.language.clicked.connect(self.language_hook)
            
            profile = main_paras.info.getProfile(main_paras.sign_in_user)
            self.user_id_show.setText(main_paras.sign_in_user)
            self.place_show.setText(profile['place'])
            self.city_show.setText(profile['city'])
            self.country_show.setText(profile['country'])
            self.provider_show.setText(profile['provider'])
            if main_paras.info.getTestMode() == TEST_MODE_SPEED:
                self.testing_mode_show.setText(self.tr('SPEED'))
            else:
                self.testing_mode_show.setText(self.tr('NORMAL'))

        except Exception as error:
            print(error)

    def change_psw_hook(self):
        try:
            global popUp
            popUp = _ChangePassword()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
            pass
        except Exception as error:
            print(error)

    def language_hook(self):
        try:
            global popUp
            popUp = _Language()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
            pass
        except Exception as error:
            print(error)


if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_ProfileDetail()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
