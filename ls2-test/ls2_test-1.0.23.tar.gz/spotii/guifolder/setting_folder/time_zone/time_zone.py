import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import pytz
import time
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
class _TimeZone(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_TimeZone, self).__init__(parent)

        self.first = True
        loadUi(os.path.join(currentdir,'time_zone.ui'),self)
        self.config()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
    def config(self):
        try:
            
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close)

            currentZone = main_paras.info.getTimeZone()
            if currentZone not in pytz.all_timezones:
                main_paras.info.setDefaultTimeZone()
                currentZone = main_paras.info.getTimeZone()

            self.time_zone_list.setStyleSheet("combobox-popup: 0;")
            self.time_zone_list.currentTextChanged.connect(self.on_time_zone_changed)
            self.time_zone_list.view().setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
            
            self.time_zone_list.addItems(pytz.all_timezones)
##            current = main_paras.info.getCurrentLanguage()
##            print(current)
            self.first = True
            self.time_zone_list.setCurrentIndex(self.time_zone_list.findText(currentZone));
            main_paras.info.setTimeZone(currentZone)
            #self.on_time_zone_changed()
            #drop_down
            #self.time_zone_list.setMaxVisibleItems(10)
            
            pass
        except Exception as error:
            print(error)
            


    def save_bt_hook(self):
        try:
##            main_paras.info.setCurrentLanguage(self.language.currentIndex())
##            self.close()
##            main_paras.queueForGui.put([LANGUAGE_CHANGE_INDEX, 0, '', '', ''])
            
            pass
                
        except Exception as error:
            print(error)

    def on_time_zone_changed(self):
        try:
            if self.first:
                self.first = False;
                return
            current = str(self.time_zone_list.currentText())
            main_paras.info.setTimeZone(current)
#             print ('Before: ', time.strftime('%X %x %Z'))
#             current = str(self.time_zone_list.currentText())
#             os.environ['TZ'] = current
#             main_paras.info.setTimeZone(current)
#             if sys.platform == 'linux':
#                 time.tzset()
#             print ('After: ', time.strftime('%X %x %Z'))
#             pass
                
        except Exception as error:
            print(error)
            
##>>> time.strftime('%X %x %Z')
##'12:45:20 08/19/09 CDT'
##>>> os.environ['TZ'] = 'Europe/London'
##>>> time.tzset()
##>>> time.strftime('%X %x %Z')
            

if __name__ == "__main__":    
    app = QtWidgets.QApplication(sys.argv)
    QtWidgets.QMainWindow
    window=_TimeZone()
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
