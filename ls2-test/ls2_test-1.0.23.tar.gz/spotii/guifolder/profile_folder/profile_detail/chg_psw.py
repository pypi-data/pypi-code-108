import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0, currentdir)
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
import wrong_password
from vkeyboard import handleVisibleChanged


class _ChangePassword(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_ChangePassword, self).__init__(parent)


        loadUi(os.path.join(currentdir,'chg_psw.ui'),self)
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
            self.change_psw.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.change_psw.clicked.connect(self.change_psw_hook)
            pass
        except Exception as error:
            print(error)

    def change_psw_hook(self):
        try:
            global popUp
            psw = self.current_psw.text()
            new_psw= self.new_psw.text()
            confirm_psw=self.confirm_psw.text()

            popUp = wrong_password._WrongPassword()            
            if new_psw != confirm_psw:
                popUp.setMessage(self.tr("new password doesn't match."))
            elif psw == '' or new_psw =='' or confirm_psw =='':
                popUp.setMessage(self.tr("Can not be empty."))                
            else:
                main_paras.queueForCom.put([CHG_PSW, psw, new_psw])
                response=main_paras.api_result_que.getTimeout(10)
                print('change_psw_hook response: ',response)
                ##[NON_SLOT_INDEX, API_RESPONSE_FAIL,  parsing[CODE], parsing[RSLT]] "spotii/communication/sign_up.py"
                ##[5, 1, '0', 'User ID exist.']
                if response == None:
                    popUp.setMessage(self.tr("Sign in/Check network."))
                elif response[1] == API_RESPONSE_FAIL:
                    popUp.setMessage(self.tr(response[3]))
                elif response[1] == API_RESPONSE_SUCCESS:
                    self.close()
                    popUp.setMessage(self.tr(response[3]),self.tr('Ok'))
                else:
                    popUp.setMessage(self.tr("Something wrong!"))
            x,y = getMainTopLeft()
            popUp.move(x,y)
            popUp.show()
           
        except Exception as error:
            print(error)
    def closeEvent(self,event):
        print("Pop dialog is closing")


if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
##    trans=QTranslator()
##    trans.load("gui.qm")
    
    #qForGui=queue.Queue()
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    QtWidgets.QMainWindow
    window=_ChangePassword()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
