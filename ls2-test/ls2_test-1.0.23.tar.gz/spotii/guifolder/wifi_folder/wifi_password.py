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
import main_paras
import wifi_setting
import wifi_list
import wrong_password


class _WifiPassword(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_WifiPassword, self).__init__(parent)

        self.originalTitleX = 0
        self.originalTitleY = 0

        self.newPassword =''
        self.wifiName =''
        loadUi(os.path.join(currentdir,'wifi_password.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        
        QtCore.QTimer.singleShot(100, self.tryToConnect)
        self.original = True        

    def keyUp(self):
        print('keyUp got emit')
        if self.original:
            self.original = False
            self.move(0,0)
            self.repaint()

    def config(self):
        try:
            main_paras.keyboard_up.signal.connect(self.keyUp)
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.back_up)

            self.connect_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.connect_bt.clicked.connect(self.connect_bt_hook)
            pass
        except Exception as error:
            print(error)

    def setName(self, name):
        self.title.setText('Wi-Fi:'+name)
        self.wifiName = name
        self.originalTitleX = self.title.x()
        self.originalTitleY = self.title.y()
    def connect_bt_hook(self):
        try:
            self.setConnectingInfo()
            self.newPassword=self.password.text()            
            if wifi_setting.wifiConnect(self.wifiName,self.newPassword):
                print('network connected')
                self.back_up()
            else:
                self.setToDefault()
                popUp = wrong_password._WrongPassword()
                x,y = getMainTopLeft()
                popUp.move(x,y)
                popUp.exec()
 
        except Exception as error:
            print(error)
    def back_up(self):
        self.close()
        global popUp
        popUp = wifi_list._WifiList()
        x,y = getMainTopLeft()
        popUp.move(x+225, y-7)
        popUp.show()
    def setConnectingInfo(self):
        self.connect_bt.hide()
        self.password.hide()
        self.password_hit.hide()
        self.back.hide()
        self.title.move(self.originalTitleX-20, self.originalTitleY+80)
        self.title.setText('Connecting:'+self.wifiName)
        self.repaint()
        
    def setToDefault(self):
        self.connect_bt.setVisible(True)
        self.password.setVisible(True)
        self.password_hit.setVisible(True)
        self.back.setVisible(True)
        self.title.move(self.originalTitleX, self.originalTitleY)
        self.title.setText('Wi-Fi:'+self.wifiName)
        
        
    def tryToConnect(self):
        self.setConnectingInfo()
        #print('tryToConnect',self.wifiName)
        if wifi_setting.wifiConnect(self.wifiName):
            self.back_up()
        else:
            #print('connect failed')
            self.setToDefault()

    def closeEvent(self,event):
        print("_WifiPassword is closing")
#        main_paras.type_in_que.put([self.passwordIsSet, self.newPassword])
        
    

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)
#    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    #QtWidgets.QMainWindow
    window=_WifiPassword()
    window.show()
#    window.exec()

    print(window.result())
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
