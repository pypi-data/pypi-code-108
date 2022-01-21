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
from main_paras import getMainTopLeft
import main_paras
from profile_detail.profile_detail import _ProfileDetail
from sign_detail.sign_in import _SignIn
from profile_detail.test_report import _TestReport
from wrong_password import _WrongPassword


class _ProfileDialog(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_ProfileDialog, self).__init__(parent)


        loadUi(os.path.join(currentdir,'profile_wrap.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(93, 89)
        

    def closeEvent(self,event):
        print("_ProfileDialog is closing")

    def config(self):
        try:
            self.profile_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.profile_bt.clicked.connect(self.profile_hook)

            self.report_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.report_bt.clicked.connect(self.report_hook)

            self.sign_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.sign_bt.clicked.connect(self.sign_hook)

            if main_paras.signedIn():
                self.sign_bt.setText(self.tr('Sign Out'))
            else:
                self.sign_bt.setText(self.tr('Sign In'))
        
            pass
        except Exception as error:
            print(error)

    def profile_hook(self):
        try:
            #global popUp
            self.close()
            popUp = _ProfileDetail()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.exec()
            pass
        except Exception as error:
            print(error)

    def report_hook(self):
        try:
            global popUp
            self.close()
            if main_paras.sign_in_token !='':
                popUp = _TestReport()
            else:
                popUp = _WrongPassword()
                popUp.setMessage(self.tr("Sign in and enter basic test information."),self.tr('Ok'))
                
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
                
        except Exception as error:
            print(error)

    def sign_hook(self):
        try:
            global popUp
            if not main_paras.signedIn():
                self.close()
                popUp = _SignIn()
            else :
                main_paras.singn_out_clear()                
                self.sign_bt.setText(self.tr('Sign In'))
                self.close()
                popUp = _WrongPassword()
                popUp.setMessage(self.tr("The user has signed out"),self.tr('Done'))
                
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
                
        except Exception as error:
            print('sign_hook',error)

            

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_ProfileDialog()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
