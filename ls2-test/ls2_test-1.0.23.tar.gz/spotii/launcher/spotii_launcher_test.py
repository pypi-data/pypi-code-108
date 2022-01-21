import threading
import queue
import time
import os
import subprocess
from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
print(currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
print(parentdir)


from launcher import _Launcher

LAUNCHER_VERSION = 'spotii_launcher_1.04\r\n'
TIME_LIMIT = 100
CLOSE_EVENT = 'close'
JOB_DONE = 'job_done'

TASK_ONE_MILESTONE= 30
TASK_TWO_MILESTONE= 50
TASK_THREE_MILESTONE= 70
TASK_FOUR_MILESTONE= 90
TASK_FIVE_MILESTONE= 95
TASK_FINAL_MILESTONE= 98

class NotifyThread(QtCore.QThread):
    signal_to_Gui  = QtCore.pyqtSignal(object)
    signal_to_Thread = QtCore.pyqtSignal(object)
    signal_to_Window = QtCore.pyqtSignal(object)

class FunctionThread(QtCore.QThread):
    def __init__(self, emitThread):
        super(FunctionThread, self).__init__()
        self.emitThread=emitThread
        self.emitThread.signal_to_Thread.connect(self.signalHook)
        self.running=True
        self.done = False
    def signalHook(self,item):
        if item == CLOSE_EVENT:
            self.running = False
        elif item == JOB_DONE:
            self.done = True

class TimerThread(FunctionThread):
    def __init__(self, emitThread):
        super(TimerThread, self).__init__(emitThread)
    def run(self):                
        count = 0
        while count < TIME_LIMIT and self.running:
            count +=1
            #print("in TimerThread", count)
            if self.done:
                time.sleep(0.5)
            elif count < TASK_ONE_MILESTONE:
                time.sleep(0.1)
            elif count < TASK_TWO_MILESTONE:
                time.sleep(0.5)
            elif count < TASK_THREE_MILESTONE:
                time.sleep(0.9)
            elif count < TASK_FOUR_MILESTONE:
                time.sleep(1.5)
            elif count < TASK_FIVE_MILESTONE:
                time.sleep(5)
            else :
                time.sleep(15)
            
            
            self.emitThread.signal_to_Gui.emit(1)
        print('TimerThread done')
def pre_install():
    try:
        upgrade=subprocess.check_output(['pip3','show','pytz','--disable-pip-version-check']).decode("utf-8")
        print(upgrade)
    except Exception as e:
        print('pytz show exception: ',e)
        try:
            upgrade=subprocess.check_output(['pip3','install','pytz','--disable-pip-version-check']).decode("utf-8")
            print(upgrade)
        except Exception as e:
            print('pytz install exception:',e)
    
class JobThread(FunctionThread):
    def __init__(self, emitThread):
        super(JobThread, self).__init__(emitThread)
    def run(self):                
        #print("Start emit thread")
        count = 0
        time.sleep(0.1)
        self.emitThread.signal_to_Gui.emit([LAUNCHER_VERSION,0])
        while True:
            self.emitThread.signal_to_Gui.emit(['Checking...\r\n',1])
            upgrade ='Nothing'
            try:
#                upgrade=subprocess.check_output(['pip3','install','spotii','-U', '--disable-pip-version-check']).decode("utf-8")
                upgrade=subprocess.check_output(['pip3','install','ls2_test','-U', '--disable-pip-version-check']).decode("utf-8")
            except subprocess.CalledProcessError as e:
                print('subprocess error',e.output)
            except ConnectionError as e:
                print('connection error',e)
            except Exception as e:
                print('Exception',e)
            #pre_install()
            #time.sleep(10)
            #print('upgrade:',upgrade)
#             self.emitThread.signal_to_Gui.emit([upgrade,TASK_ONE_MILESTONE])
# 
# ##            if not self.running:
# ##                break;
#             self.emitThread.signal_to_Gui.emit(['Initializing...\r\n',TASK_ONE_MILESTONE+1])
            self.emitThread.signal_to_Gui.emit(['Starting...\r\n',TASK_FINAL_MILESTONE])
            self.emitThread.signal_to_Thread.emit(JOB_DONE)
            
            break;
        print('JobThread done')
            
class MyUi(_Launcher):
    def __init__(self, emitThread):
        super(MyUi, self).__init__()
        self.emitThread=emitThread
        self.emitThread.signal_to_Gui.connect(self.emitHook)
        self.emitThread.signal_to_Window.connect(self.windowSignalHook)

        self.timerThread=TimerThread(self.emitThread)
        self.timerThread.start()

        self.jobThread=JobThread(self.emitThread)
        self.jobThread.start()
        self.count=0
        self.initDone=False
 
    def setupParts(self):
        pass

    def emitHook(self,item):
        try:
            if type(item) == int:
                if item != TASK_FINAL_MILESTONE -1 :
                    self.count+=item
            else:
                self.count=item[1]
                self.label.setText(self.label.text()+item[0])
            self.progressBar.setProperty("value", self.count)
            if self.count == 100:
                print(self.count)
                self.emitThread.signal_to_Thread.emit(CLOSE_EVENT)
                self.initDone=True
                #self.close()
                QtWidgets.qApp.quit()
#                 self.emitThread.signal_to_Window.emit(CLOSE_EVENT)
        except Exception as e:
            print(e)
            
    def windowSignalHook(self, item):
        print('windowSignalHook',item)
        if item ==CLOSE_EVENT:
            self.emitThread.signal_to_Thread.emit(CLOSE_EVENT)
            
            #QtWidgets.qApp.quit()
            #time.sleep(1.5)
            self.initDone=True
            self.close()
    def status(self):
        return self.initDone
        

if __name__ == "__main__":
    import sys
    __emitThread=NotifyThread()
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MyUi(__emitThread) ##QtWidgets.QMainWindow()
    
    MainWindow.show()
    returnValue =app.exec_()
    print('launcher return value :' ,returnValue)
    initialized = MainWindow.status()
    
    
    if returnValue == 0 and initialized:
        
        #MainWindow.close()
        try:
            from spotii import spot_main
        except Exception as e:
            print(e)
            from main import spot_main
        print('init done, start spot_main')
        spot_main()
        
    else:
        sys.exit(0)
