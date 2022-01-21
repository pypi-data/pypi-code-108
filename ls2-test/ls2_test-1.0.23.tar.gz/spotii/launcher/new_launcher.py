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

import launcher_resource


class _Launcher(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(_Launcher, self).__init__(parent)

        loadUi(os.path.join(currentdir,'launcher.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        
#        QtCore.QTimer.singleShot(100, self.tryToConnect)

    def config(self):
        try:
            
##            style = '.QWidget{background-image:url(:/slot/png/slot/'+self.slotBasic[page][0]+ ');border:0px}'
##            self.centralwidget.setStyleSheet(style)
            pass
        except Exception as error:
            print(error)

    def closeEvent(self,event):
        print("_WifiPassword is closing")
#        main_paras.type_in_que.put([self.passwordIsSet, self.newPassword])
        
    

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)
#    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)

    #QtWidgets.QMainWindow
    window=_Launcher()
    window.show()

    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
