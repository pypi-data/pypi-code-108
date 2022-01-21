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
import sign_in
import wrong_password
from vkeyboard import handleVisibleChanged

class _CreateAccount(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_CreateAccount, self).__init__(parent)
        
        loadUi(os.path.join(currentdir,'create_new_account.ui'),self)
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
            self.sign_in_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
            self.create_account.clicked.connect(self.create_account_hook)
            self.sign_in_bt.clicked.connect(self.sign_in_bt_hook)


#             self.email.installEventFilter(self)
#             self.first_name.installEventFilter(self)
#             self.last_name.installEventFilter(self)
#             self.password.installEventFilter(self)
#             self.confirm_psw.installEventFilter(self)

            
            pass
        except Exception as error:
            print(error)

    def create_account_hook(self):
        global popUp
        try:
            user = self.email.text()
            psw =  self.password.text()
            firstName = self.first_name.text()
            lastName =self.last_name.text()
            confirm_psw = self.confirm_psw.text()
            popUp = wrong_password._WrongPassword()
            if psw != confirm_psw:
                popUp.setMessage(self.tr("password doesn't match."))
            elif user == '' or psw == '' or firstName =='' or lastName =='':
                popUp.setMessage(self.tr("Can not be empty."))                
            else:
                main_paras.queueForCom.put([SIGN_UP, user, psw, firstName, lastName])
                response=main_paras.api_result_que.getTimeout(10)
                print('create_account response: ',response)
                ##[NON_SLOT_INDEX, API_RESPONSE_FAIL,  parsing[CODE], parsing[RSLT]] "spotii/communication/sign_up.py"
                ##[5, 1, '0', 'User ID exist.']
                if response == None:
                    popUp.setMessage(self.tr("Check network."))
                elif response[1] == API_RESPONSE_FAIL:
                    popUp.setMessage(self.tr(response[3]))
                elif response[1] == API_RESPONSE_SUCCESS:
                    self.close()
                    popUp.setMessage(self.tr("Check your e-mail to validate the account."),self.tr('Ok'))
                else:
                    popUp.setMessage(self.tr("Something wrong!"))
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
        except Exception as error:
            print(error)
    def sign_in_bt_hook(self):
        try:
            global popUp
            self.close()
            popUp =sign_in. _SignIn()
            x,y = getMainTopLeft()
            popUp.move(x,y)
            #popUp.exec()
            popUp.show()
            pass
        except Exception as error:
            print(error)

    def closeEvent(self,event):
        print("_CreateAccount is closing")

    def eventFilter(self, source, event):
#         if event.type() == QtCore.QEvent.FocusIn and \
#            (
#                source == self.email 
#             or source == self.first_name
#             or source == self.last_name
#             or source == self.password
#             or source == self.confirm_psw
#                ):
#             if self.original:
#                 self.original = False
#                 self.scroll.setVisible(True)
#                 self.move(0,0)
#                 self.repaint()
#             print("A")
        return super(_CreateAccount, self).eventFilter(source, event)

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    QtWidgets.QMainWindow
    window=_CreateAccount()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
