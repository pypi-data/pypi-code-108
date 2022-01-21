import os
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import subprocess
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
import title_rc

#myprocess =None
class _Play(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_Play, self).__init__(parent)
        loadUi(os.path.join(currentdir,'video.ui'),self)
        self.pollingTimer = QtCore.QTimer()
        self.process = None
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        QtCore.QTimer.singleShot(0, self.play)
 
    def config(self):
        try:
            self.back.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
            self.back.clicked.connect(self.close_now)
            self.pollingTimer.timeout.connect(self.processPolling)
            
        except Exception as error:
            print(error)
    def close_now(self):
        try:
            #myprocess.stdin.write(b'q')
            #self.myprocess.kill()
            #self.myprocess.terminate()
            subprocess.call(['pkill','omx'])
            self.close()
        except Exception as error:
            print(error)
    def play(self):
#        omxplayer -o local --win "0 0 470 262" 2.mp4
        #global myprocess
#        myprocess = subprocess.Popen(['omxplayer','-b','-o','local','--win','\"0 100 470 272\"','/home/pi/vids/2.mp4'],
        self.process=subprocess.Popen(['omxplayer','-o','local','--win','0 30 480 272','/home/pi/app/spotii/launcher/look_spot_2.mp4'],
                                     stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE, close_fds=True)
        print(self.process.poll())
#        self.myprocess = subprocess.Popen(['omxplayer','-b','/home/pi/vids/2.mp4'],stdin=subprocess.PIPE)
        self.pollingTimer.start(1)
    def processPolling(self):
        
        if self.process.poll() != None:
            print('process done', self.process.poll())
            self.pollingTimer.stop()
            self.close()

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    play=_Play()
    
    drtn=play.exec()
    print('pop dialog end',drtn)
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
