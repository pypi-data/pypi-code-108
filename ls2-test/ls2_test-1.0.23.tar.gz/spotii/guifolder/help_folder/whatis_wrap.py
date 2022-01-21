import os
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
grandparentdir = os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)
import title_rc

        
class _Whatis(QtWidgets.QDialog):
    def __init__(self,title,html,parent=None):
        super(_Whatis, self).__init__(parent)
        self.html=html
        loadUi(os.path.join(currentdir,'whatis.ui'),self)
        self.title.setText(title)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        self.show_html(self.html)

    def config(self):
        try:
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
#            self.textBrowser.setText('hello')
            
        except Exception as error:
            print(error)

    def show_html(self,html_file):
        try:
            with open(html_file, 'r' ,encoding='unicode_escape') as fh:
                self.textBrowser.insertHtml(fh.read())
            QtCore.QTimer.singleShot(0, self.setTextBrowserTop)
        except Exception as error:
            print(error)
        
    def setTextBrowserTop(self):
        vBar=self.textBrowser.verticalScrollBar()
        vBar.setValue(0)


if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    whatis=_Whatis('Legal',os.path.join(currentdir,'legal.html'))
    
    drtn=whatis.exec()
    print('pop dialog end',drtn)
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
