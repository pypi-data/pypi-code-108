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
import wrong_password
from vkeyboard import handleVisibleChanged

class _TestReport(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_TestReport, self).__init__(parent)


        loadUi(os.path.join(currentdir,'test_report.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.last_scroll_value=0
        self.original = True
        self.sendRequest = False

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
            self.save_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.send_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            
            self.save_bt.clicked.connect(self.save_bt_hook)
            self.send_bt.clicked.connect(self.send_bt_hook)

            self.get_report_email()
            
            self.email.setText(main_paras.report_email_1)
            self.email_2.setText(main_paras.report_email_2)
        except Exception as error:
            print(error)

    def get_report_email(self):
        try:
            main_paras.api_result_que.clear()
            main_paras.queueForCom.put([GET_REPORT_EMAIL])
            response=main_paras.api_result_que.getTimeout(10)
            #print('get_report_email:',response)
            if response[1] == API_RESPONSE_SUCCESS:
                main_paras.report_email_1=response[2]
                main_paras.report_email_2=response[3]
        except Exception as error:
            print(error)
        

    def send_bt_hook(self):
        try:
            global popUp
            email_1 = self.email.text()
            email_2 = self.email_2.text()

            if (email_1 == '' and email_2=='') or (email_1!=main_paras.report_email_1) or (email_2!=main_paras.report_email_2):
                self.sendRequest = True;
                self.save_bt.animateClick()
            else:
                popUp = wrong_password._WrongPassword()
                main_paras.queueForCom.put([GET_REPORT])
                response=main_paras.api_result_que.getTimeout(10)
                if response == None:
                    popUp.setMessage(self.tr("Check network."))
                elif response[1] == API_RESPONSE_FAIL:
                    popUp.setMessage(self.tr(response[3]))
                elif response[1] == API_RESPONSE_SUCCESS:
                    popUp.setMessage(self.tr(response[3]), self.tr('Ok'))
                x,y = getMainTopLeft()
                popUp.move(x,y)
                popUp.show()
                
        except Exception as error:
            print(error)
            
#if (email_1 != '' and email_1.count('@') == 1) or (email_2 != '' and email_2.count('@') == 1):

    def save_bt_hook(self):
        try:
            global popUp
            popUp = wrong_password._WrongPassword()
            email_1 = self.email.text()
            email_2 = self.email_2.text()
            saved = False
            if (email_1 =='' and email_2 =='') or (email_1 !='' and email_1.count('@') != 1) or ( email_2 !='' and email_2.count('@') != 1):
                popUp.setMessage(self.tr("Enter correct email"))
            else:
                main_paras.report_email_1 = self.email.text()
                main_paras.report_email_2 = self.email_2.text()
                main_paras.queueForCom.put([TEST_REPORT_EMAIL, email_1, email_2])
                response=main_paras.api_result_que.getTimeout(10)
                if response == None:
                    popUp.setMessage(self.tr("Check network."))
                elif response[1] == API_RESPONSE_FAIL:
                    popUp.setMessage(self.tr(response[3]))
                elif response[1] == API_RESPONSE_SUCCESS:
                    popUp.setMessage(self.tr(response[3]), self.tr('Saved'))
                    saved = True
                
            x,y = getMainTopLeft()
            popUp.move(x,y)
            
            
            if saved == True and self.sendRequest == True:
                self.sendRequest = False
                self.send_bt.animateClick()
                popUp.close()
            else:
                popUp.show()
                
        except Exception as error:
            print(error)
    
    def closeEvent(self,event):
        print("_ForgotPassword is closing")


if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)
#    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)


    QtWidgets.QMainWindow
    window=_TestReport()
    window.move(0,0)
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
