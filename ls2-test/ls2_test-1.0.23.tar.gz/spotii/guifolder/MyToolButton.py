from PyQt5 import Qt, QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDateTime
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QFont
import time
class MyToolButton(QtWidgets.QToolButton):
    def __init__(self, parent=None):
        super(MyToolButton,self).__init__(parent)
        self.activeIcon=None
        self.inactiveIcon=None
        self.setStyleSheet("QToolButton{background-color: transparent; border:0; color : white}")
        #self.setAutoRaise(True)
        #self.setAutoFillBackground(True)

        self.enterTimeStamp=0
        self.notifyTimeStamp=0
        self.clicked.connect(self.beClicked)
        self.PopWindow=None
        self.popX=0
        self.popY=0
        
    def setup(self, PopWindow, x, y):
        try:
            print('setting up...')
            self.PopWindow=PopWindow
            self.popX=x
            self.popY=y
        except Exception as e:
            print(e)
        
    def beClicked(self):
        try:
            print('beClicked')
            if self.isChecked():
                if self.iconClickAgain():
                    self.clearNotify()
                    self.setChecked(False)
                    #self.setEnabled(False)
                    #self.setCheckable(True)
                else:
                    assert self.PopWindow != None
                    popUp= self.PopWindow()
                    popUp.move(self.popX, self.popY)
                    popUp.exec()
                    self.setChecked(False)
                    #self.setEnabled(False)
                    #self.setCheckable(True)
                    self.notify()            
        except Exception as e:
            print(e)
        
    def enterEvent(self, event):
        try:
            self.enterTimeStamp=time.time()
            #print("Mouse entered",self.enterTimeStamp)
            super(MyToolButton, self).enterEvent(event)
        except Exception as e:
            print(e)
##        self.setStyleSheet("QToolButton{background-color: rgba(0,21,59,255);}")
##        icon = QtGui.QIcon()
##        icon.addPixmap(self.activeIcon, QtGui.QIcon.Normal, QtGui.QIcon.Off)
##        self.setIcon(icon)
##        self.repaint()
##        # emit your signal
    def leaveEvent(self, event):
        try:
            #print("Mouse left",time.time())
            super(MyToolButton, self).leaveEvent(event)
        except Exception as e:
            print(e)
##        self.setStyleSheet("QToolButton{background-color: transparent; border:0; color : white}")
##        if self.isChecked():
##            return
##        icon = QtGui.QIcon()
##        icon.addPixmap(self.inactiveIcon, QtGui.QIcon.Normal, QtGui.QIcon.Off)
##        self.setIcon(icon)
##        self.repaint()
            
##    def actionEvent(self, event):
##        print('actionEvent', event)
##        mouceReleaseEvent
##        
##    def changedEvent(self, event):
##        print('changedEvent', event)
##        super(MyToolButton, self).changedEvent(event)
        
##    def hitButton(self, event):
##        print('hitButton', event)
##        super(MyToolButton, self).hitButton(event)
        
##    def moucePressEvent(self, event):
##        print('moucePressEvent', event)
##        super(MyToolButton, self).moucePressEvent(event)
##        
##    def mouceReleaseEvent(self, event):
##        print('mouceReleaseEvent', event)
##        super(MyToolButton, self).mouceReleaseEvent(event)

    def notify(self):
        try:
            self.notifyTimeStamp=time.time()
            #print('got it',self.notifyTimeStamp)
        except Exception as e:
            print(e)
    def clearNotify(self):
        self.notifyTimeStamp = 0
    def iconClickAgain(self):
        if self.notifyTimeStamp!=0 and self.enterTimeStamp!=0:
            if abs(self.enterTimeStamp - self.notifyTimeStamp) < 0.1 :
                return True
        return False
