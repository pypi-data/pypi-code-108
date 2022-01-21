import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
import time
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
#from SlotPage import SlotPage
from slot.scan import _Scan
from slot.empty import _Empty
from slot.detecting import _Detecting
from slot.warning import _Warning
from slot.positive import _Positive
from slot.negative import _Negative
from slot.invalid import _Invalid
from slot.flip import _Flip
from slot.invalid_qr import _Invalid_qr

import title_rc
from emit_thread import SignalThread
#from main_paras import mainChannelNotify, getDetectionMode
from main_paras import mainChannelNotify, getDetectionMode, setOperation
from main_paras import queueForGui, queueForResult, queueForCom
#from test_handler.cassette_polling import CassettePolling
from define import *
import main_paras


class PageResponse(QtCore.QThread):
    signal = QtCore.pyqtSignal(object)



class MyStackedWidget(QtWidgets.QStackedWidget):
    def __init__(self,parent=None):
        super(MyStackedWidget, self).__init__(parent)
        self.button_hooks=[None,None,None,None,None,None,self.scanHook,self.flipHook,self.invalidQrHook]
        
        self.slotBasic = [
           (None,                self.empty,),
           (None,                self.warning,),
           (None,                self.detecting,),
           (None,                self.positive,),
           (None,                self.negative,),
           (None,                self.invalid,),
           (self.scanHook,       self.scan,),
           (self.flipHook,       self.flip,),
           (self.invalidQrHook,  self.invalid_qr,),
            ]
        self.slot_no = 0
        self.cassetteId=""
        self.timeLeft = TIMER_DURATION
        self.timeIncreasing = 0
        self.myTimer = QtCore.QTimer()
        self.myTimer.timeout.connect(self.timer_timeout)
        
        self.ready=False
        self.i2c=None
        self.camera=None
        self.function=None
#         self.pageResponse = PageResponse()
#         self.pageResponse.signal.connect(self.emitHook)
        self.pageParking = SignalThread()
        self.pollingTimer=QtCore.QTimer()
        self.pollingTimer.timeout.connect(self.polling_repeat)
        
        loadUi(os.path.join(currentdir,'myStackedWidget.ui'),self)
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        self.resize(96, 224)
        
        
    def polling_repeat(self):
        self.pageParking.signal.emit(time.time())
        #print(self.slot_no, time.time(),self.pageParking.signal)
        self.pollingTimer.start(1000)
        
        
    def empty(self, item):
        print(self.slot_no, 'empty', item)
    def warning(self, item):
        print(self.slot_no, 'warning', item)
    def detecting(self, item):
        print(self.slot_no, 'detecting', item)
    def positive(self, item):
        print(self.slot_no, 'positive', item)
    def negative(self, item):
        print(self.slot_no, 'negative', item)
    def invalid(self, item):
        print(self.slot_no, 'invalid', item)
    def scan(self, item):
        print(self.slot_no, 'scan', item)
    def flip(self, item):
        print(self.slot_no, 'flip', item)
    def invalid_qr(self, item):
        print(self.slot_no, 'invalid_qr', item)
        
    def scanHook(self):
        print('scanHook', self.slot_no)
        if not main_paras.signedIn():
            main_paras.queueForGui.put([SIGN_IN_FIRST_INDEX,'','',''])
            return
        setOperation(self.slot_no ,MANUAL_OPERATION_SCAN)
    def flipHook(self):
        print('flipHook', self.slot_no)
        setOperation(self.slot_no ,MANUAL_OPERATION_START_TESTING)
    def invalidQrHook(self):
        print('invalidQrHook', self.slot_no)
        setOperation(self.slot_no ,MANUAL_OPERATION_START)

    def setSlotNo(self,number):
        try:
            assert(number >= 0 and number <=4), "Wrong slot number"
            self.slot_no = number
            for page in range(0, len(self.slotBasic)):
                self.setCurrentIndex(page)
                self.currentWidget().setDetail(self.slot_no)
                self.currentWidget().buttonHook(self.slotBasic[page][0])
            self.ready=True
            
            self.setCurrentIndex(0)
            #self.pollingTimer.start()
        except Exception as error:
            print(error)
        except AssertionError as e:
            raise Exception( e.args )

    def config(self):
        try:
            #self.currentChanged.connect(self.onChanged)
            pass
        except Exception as error:
            print(error)

#     def emitHook(self,item):
#         try:
#             print(time.strftime('%Y%m%d%H%M%S'),"emitHook:",item)
#             slotNo  = item[0]
#             errCode = item[1]
#             qrCode  = item[2]
#             if slotNo == NON_SLOT_INDEX:
#                 for i in range(TOTAL_SLOTS):
#                     self.setStatus(SLOT_STATUS_WARNING, 'CR Error')
#             elif errCode == DEVICE_STATE_TAKING_PHOTO:
#                 self.detecting_(qrCode)
#             elif errCode == Positive_test_result:
#                 self.setStatus(SLOT_STATUS_POSITIVE, qrCode)
#             elif errCode == Negative_test_result:
#                 self.setStatus(SLOT_STATUS_NEGATIVE, qrCode)
#             elif errCode == Invalid_image_identifier:
#                 self.setStatus(SLOT_STATUS_INVALID, qrCode)
#             elif errCode == DEVICE_STATE_CASSETTE_EMPTY:
#                 self.setStatus(SLOT_STATUS_EMPTY, qrCode)
#             else:
#                 self.setStatus(SLOT_STATUS_WARNING, qrCode)
#         except Exception as e:
#             print(e)
    def setStatus(self, status_index, cassette, time=None):
        try:
            
            
            self.cassetteId=cassette
            self.setCurrentIndex(status_index)
            page=self.currentWidget()
            try:        ## some pages don't have id
                page.id.setText(self.cassetteId)
            except:
                pass
            if(time!=None):
                page.timer.setText(time) ## 1 for counting down timer
            else:
                self.myTimer.stop()
        except Exception as e:
            print (e)

    def detecting_(self, cassette):
        try:
            self.cassetteId=cassette
            self.timeLeft = TIMER_DURATION
            self.timeIncreasing = 0
            self.myTimer.start(1000)
            self.showDetecting()
        except Exception as e:
            print(e)

    def timer_timeout(self):
        try:
            self.timeLeft -= 1
            self.timeIncreasing += 1
            self.showDetecting()        
            if self.timeLeft == 0:
                self.detection_timeout()
                self.timeIncreasing = 0
                self.myTimer.stop()
        except Exception as e:
            print(e)
        
    def showDetecting(self):
        try:
            self.setStatus(SLOT_STATUS_DETECTING, self.cassetteId, time.strftime('%-M:%S', time.gmtime(self.timeIncreasing)))
        except Exception as e:
            print(e)
    def detection_timeout(self):
        try:
            self.setStatus(SLOT_STATUS_WARNING, self.cassetteId)
        except Exception as e:
            print(e)

    def onChanged(self, index):
        if self.ready :
            try:
                self.pageParking.signal.disconnect()
            except Exception:
                pass
            self.pageParking.signal.connect(self.slotBasic[index][1])
            
    def totalPage(self):
        return len(self.slotBasic)

if __name__ == "__main__":
    import sys
    
    app = QtWidgets.QApplication(sys.argv)

    QtWidgets.QMainWindow
    window=MyStackedWidget()
    window.show()
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
