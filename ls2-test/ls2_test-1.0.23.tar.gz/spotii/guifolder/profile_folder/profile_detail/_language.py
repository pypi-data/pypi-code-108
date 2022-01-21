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



drop_down = 'QComboBox.drop-down {\
    subcontrol-origin: padding;\
    subcontrol-position: top right;\
    width: 60px;\
\
    border-left-width: 1px;\
    border-left-color: black;\
    border-left-style: solid; \
    border-top-right-radius: 3px; \
    border-bottom-right-radius: 3px;\
}'
class _Language(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_Language, self).__init__(parent)


        loadUi(os.path.join(currentdir,'language.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
    def config(self):
        try:
            
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)
            self.save_bt.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.save_bt.clicked.connect(self.save_bt_hook)

#            self.language.currentIndexChanged.connect(self.language_changed)
#            self.language.setStyleSheet(drop_down)
            self.language.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            self.language.addItems(main_paras.info.getLanguageList())
            current = main_paras.info.getCurrentLanguage()
            print(current)
            self.language.setCurrentIndex(self.language.findText(current));
            #drop_down
#            self.language.setMaxVisibleItems(4)
            pass
        except Exception as error:
            print(error)
            

    def save_bt_hook(self):
        try:
            main_paras.info.setCurrentLanguage(self.language.currentIndex())
            self.close()
            main_paras.queueForGui.put([LANGUAGE_CHANGE_INDEX, 0, '', '', ''])
            
            pass
                
        except Exception as error:
            print(error)

    def language_changed(self):
        try:
            print('language changed')
            pass
                
        except Exception as error:
            print(error)
            
            

if __name__ == "__main__":    
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMainWindow
    window=_Language()
    window.show()    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)


##QComboBox{
##background-image: url(:/public/png/public/rectangle-copy.png);
##background-color: transparent; 
##border:0; 
##color :white; 
##selection-color:black;
##selection-background-color:white;
##combobox-popup: 0;
##
##drop-down {
##    subcontrol-origin: padding;
##    subcontrol-position: top right;
##    width: 15px;
##
##    border-left-width: 1px;
##    border-left-color: black;
##    border-left-style: solid; /* just a single line */
##    border-top-right-radius: 3px; /* same radius as the QComboBox */
##    border-bottom-right-radius: 3px;
##};
##
##}
