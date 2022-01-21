import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import subprocess
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
grandparentdir =  os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)


import title_rc
from main_paras import getMainTopLeft

class _Volume(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_Volume, self).__init__(parent)


        self.volumeHold = 0
        loadUi(os.path.join(currentdir,'volume.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setWindowFlags(flags)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.resize(146, 62)
        

    def closeEvent(self,event):
        try:
            if self.mute.isChecked():
                setVolume = self.volumeHold
            else:
                setVolume = self.slider.value()
            cmd = 'amixer set \'Master\''+' '+str(setVolume)+'%'
            print(cmd)
            subprocess.run([cmd], shell=True)
        except Exception as e:
            print(e)
        print("_Volume is closing")

    def config(self):
        try:
            self.mute.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.slider.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.mute.clicked.connect(self.mute_hook)
            self.slider.valueChanged.connect(self.slider_hook)
            
            result=subprocess.check_output(['amixer']).decode('utf-8').replace('\r','')
            result = result.split('Simple mixer control')
            
            gotMaster=False
            for each in result:
                if 'Master' in each:
                    gotMaster = True
                    break;
                
            volume = 100
            if gotMaster:
                #print(each)
                paraList = each.split('\n')
                #print (paraList)
                for item in paraList:
                    if 'Front Left:' in item:
                        volume = int(item[item.find('[')+1: item.find('%')])
                        print (volume)
            self.slider.setValue(volume)
            
        
            pass
        except Exception as error:
            print(error)

    def mute_hook(self):
        try:
            if self.mute.isChecked():
                self.volumeHold=self.slider.value()
                self.slider.setValue(0)
                #print('Mute')
            else:
                #print('UnMute')
                self.slider.setValue(self.volumeHold)
            pass
        except Exception as error:
            print(error)

    def slider_hook(self, value):
        try:
            pass
        except Exception as error:
            print(error)            
##    def on_focusChanged(self):
##        print('focus changed')

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
    
    app = QtWidgets.QApplication(sys.argv)
    window=_Volume()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
