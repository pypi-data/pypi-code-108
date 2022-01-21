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

from define import *
import title_rc
from main_paras import getMainTopLeft
import main_paras
import create_new_account
import wrong_password
from vkeyboard import handleVisibleChanged

class _ForgotPassword(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_ForgotPassword, self).__init__(parent)


        loadUi(os.path.join(currentdir,'forgot_password.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.last_scroll_value=0
        self.original = True

    def scrolled(self):
        try:
            diff =(self.last_scroll_value - self.scroll.value())*10
            self.last_scroll_value=self.scroll.value()
            print(self.scroll.value())
            children= self.widget.findChildren(QtWidgets.QWidget)
            for child in children:
                if child != self.scroll:
                    child.move(child.pos().x(),child.pos().y()+diff)
            self.repaint()
        except Exception as error:
            print(error)

    def keyUp(self):
        print('keyUp got emit')
        if self.original:
            self.original = False
            self.scroll.setVisible(True)
            self.move(0,0)
            self.repaint()        

    def config(self):
        try:
            self.scroll.setMaximum(20)
            self.scroll.valueChanged.connect(self.scrolled)
            self.scroll.hide()
            main_paras.keyboard_up.signal.connect(self.keyUp)
            
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.create_account.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.reset_psw_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
            self.create_account.clicked.connect(self.create_account_hook)
            self.reset_psw_bt.clicked.connect(self.reset_psw_bt_hook)
            pass
        except Exception as error:
            print(error)

    def create_account_hook(self):
        try:
            global popUp
            print('create_account_hook')
            self.close()
            popUp = create_new_account._CreateAccount()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            #popUp.exec()
            popUp.show()
            pass
        except Exception as error:
            print(error)
    def reset_psw_bt_hook(self):
        try:
            global popUp
            popUp = wrong_password._WrongPassword()
            email = self.email.text()
            if email != '' and email.count('@') == 1:
                main_paras.queueForCom.put([FORGOT_PSW, email])
                response=main_paras.api_result_que.getTimeout(10)
                if response == None:
                    popUp.setMessage(self.tr("Check network."))
                elif response[1] == API_RESPONSE_FAIL:
                    popUp.setMessage(self.tr(response[3]))
                elif response[1] == API_RESPONSE_SUCCESS:
                    popUp.setMessage(self.tr("New password sent to email."))
            else:
                popUp.setMessage(self.tr("Enter correct email"))
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
                
        except Exception as error:
            print(error)

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
##    app.installTranslator(trans)
#    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)


    QtWidgets.QMainWindow
    window=_ForgotPassword()
    window.move(0,0)
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
