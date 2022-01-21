import sys
import subprocess
import threading
import time
from datetime import datetime,timezone

if __name__ == "__main__":
    import sys, os, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0, parentdir)
    
from non_block_queue import NonBlockQue
from main_paras import getDetectionMode, getOperation, setOperation, queueForGui
from test_handler.i2c_lib import i2c_device
from test_handler.take_photo import takePhoto, TakePhotoProcedure
from define import *
import main_paras


class CassettePolling(threading.Thread):
    def __init__(self, slotIndex, i2c, camera, qResult, qCom, deviceQue):
        threading.Thread.__init__(self)
        self.slotIndex = slotIndex
        self.i2c = i2c
        self.camera = camera
        self.qResult = qResult
        self.qCom = qCom
        self.deviceQue=deviceQue
        self.stopTakingPhoto = threading.Event()
        
        
        self.deviceStatus = DEVICE_STATE_ORIGINAL
        
        self.takePhotoProcedure = None
        self.running = True
        self.qrcode_que = NonBlockQue()
        self.qrPollingStamp=0
        self.manual_sequence = MANUAL_OPERATION_START
        self.prevMode=None
        self.prevCassetteStatus=None
    def stopTakePhotoProcedure(self):
        if self.takePhotoProcedure != None and self.takePhotoProcedure.is_alive():
            print("stop take photo procedure")
            self.stopTakingPhoto.set()
            self.takePhotoProcedure.join()
            self.stopTakingPhoto.clear()
            
    def startTakePhotoProcedure(self,qr_code, responeQue):
        try:
            print('start taking photo procedure', qr_code)
            if qr_code != None:
                item=[self.slotIndex, DEVICE_STATE_TAKING_PHOTO, qr_code, 'Taking photo']
                print(item)
                self.notify(item)
            self.stopTakePhotoProcedure()
            self.takePhotoProcedure = TakePhotoProcedure(self.slotIndex, qr_code, self.camera, responeQue, self.stopTakingPhoto)
            self.takePhotoProcedure.start()
        except Exception as e:
            print(e)
        
    def run(self):
        self.periodPoll()
        while self.running:
            cmd=self.deviceQue.get()
            if cmd == PHOTO_TAKING_STOP:
                #print("stop command")
                self.stopTakePhotoProcedure()
            self.deviceQue.task_done()
        else:
            #self.stopTakePhotoProcedure()
            print('polling stop', self.slotIndex)
            
#        self.cameraTest(self.index, self.i2c, self.camera)

    def notify(self, item):
#         if self.slotIndex == 0:
#             print('deviceStatus',self.deviceStatus, 'new',item[1])
        if item == CLOSE_NOW:
            self.running=False
            self.deviceQue.put(PHOTO_TAKING_STOP)
            
        elif self.deviceStatus != item[1]:
            self.deviceStatus = item[1]
            if item[1] != DEVICE_STATE_CASSETTE_POLLED:
                #print('put in queque', item)
                self.qResult.put(item)

    def cassetteOut(self):
        for i in range(5):
            i2cInstant=i2c_device(self.i2c,I2C_PORT)
            status=i2cInstant.read_data(I2C_MEM_STATUS)|0x80 #There should be bug on daughter board I2c function. sometimes missed bit 7.
            
            if status & CASSETTE_STATUS_FLAG == 0:
                print(time.strftime('%Y%m%d%H%M%S'), "Wrong flag, re-read.", self.slotIndex, hex(status))
                time.sleep(2)
                continue
            
            elif status == DEVICE_STATE_CASSETTE_EMPTY:
                break
            else:
                break
        rtn = False
#         if(self.slotIndex == 0):
#             print(self.prevCassetteStatus, status)
        if self.prevCassetteStatus != status:
            self.prevCassetteStatus=status
            if status == DEVICE_STATE_CASSETTE_EMPTY:
                print('cassette out')
                rtn = True
            
        return rtn

    def manualQr(self):
        status = DEVICE_STATE_CASSETTE_QR
        qr = None
#         if self.slotIndex ==0:
#             print('slot', self.slotIndex, 'Operation',self.manual_sequence)
            
        if self.cassetteOut() and self.manual_sequence != MANUAL_OPERATION_TEST:
            setOperation(self.slotIndex, MANUAL_OPERATION_START)
#            queueForGui.put([self.slotIndex, DEVICE_STATE_MANUAL_SCAN, '', 'cassette out'])
#            return status,qr
        
        self.manual_sequence = getOperation(self.slotIndex)
        
        if self.manual_sequence  == MANUAL_OPERATION_START:
            self.stopTakePhotoProcedure()
            self.notify([self.slotIndex, DEVICE_STATE_MANUAL_SCAN, '', 'manual scan'])
            setOperation(self.slotIndex, MANUAL_OPERATION_START_WAITING)
        if self.manual_sequence  == MANUAL_OPERATION_START_WAITING:
            pass
        elif self.manual_sequence  == MANUAL_OPERATION_SCAN:
            self.startTakePhotoProcedure(None,self.qrcode_que)
            self.qrPollingStamp=time.time()
            setOperation(self.slotIndex, MANUAL_OPERATION_GETTING_QR)
        elif self.manual_sequence  == MANUAL_OPERATION_GETTING_QR:
            qr = self.qrcode_que.get()
            if qr!=None:
                if qr != NON_QR:
                    print('got qr from image',qr)
                    self.qrCode = qr
                    setOperation(self.slotIndex, MANUAL_OPERATION_TEST)
                    self.notify([self.slotIndex, DEVICE_STATE_MANUAL_FLIP, self.qrCode, 'Waiting test'])
                else:
                    self.notify([self.slotIndex, DEVICE_STATE_MANUAL_INVALID_QR, '', 'invalid qr'])
                    setOperation(self.slotIndex, MANUAL_OPERATION_RESTART)
                    
            elif (time.time()- self.qrPollingStamp) > QR_POLLING_TIMEOUT:
                print('getting qr time out')
                self.notify([self.slotIndex, DEVICE_STATE_MANUAL_INVALID_QR, '', 'scan timeout'])
                setOperation(self.slotIndex, MANUAL_OPERATION_RESTART)
            else:
                print('reading qr...')
        elif self.manual_sequence  == MANUAL_OPERATION_TEST:
            pass
        elif self.manual_sequence  == MANUAL_OPERATION_START_TESTING:
            status = DEVICE_STATE_CASSETTE_VALID
            qr = self.qrCode
            setOperation(self.slotIndex, MANUAL_OPERATION_START_WAITING_RESULT)  ##waiting for result
        elif self.manual_sequence  == MANUAL_OPERATION_START_WAITING_RESULT:
            pass
        elif self.manual_sequence == MANUAL_OPERATION_RESTART:
            pass
        #print('manual qr')
        return status, qr
        

    def autoQr(self):
        try:
            qrCode=''
            status=DEVICE_STATE_CASSETTE_EMPTY
            for i in range(7):                
                i2cInstant=i2c_device(self.i2c,I2C_PORT)
                status=i2cInstant.read_data(I2C_MEM_STATUS)|0x80 #There should be bug on daughter board I2c function. sometimes missed bit 7.
                
                if self.slotIndex == 1 and status!=DEVICE_STATE_CASSETTE_POLLED:
                    print(hex(status), time.strftime('%Y%m%d%H%M%S'))
                qrCode=''
                if(status == DEVICE_STATE_CASSETTE_VALID):
                    qr=i2cInstant.read_block_data(I2C_MEM_ID, 9)
                    qrCode=(''.join(chr(x) for x in qr))
                    #if not qrCode.isalnum():
                    if not qrCode.isascii():
                        print(time.strftime('%Y%m%d%H%M%S'), "qrCode crashed", self.slotIndex,qrCode)
                        if i == 3:
                            i2cInstant.write_cmd(I2C_COMMAND_SYSTEM_RESET)
                        time.sleep(2)
                        continue
                    break;
                elif status & CASSETTE_STATUS_FLAG == 0:
                    print(time.strftime('%Y%m%d%H%M%S'), "Wrong flag, re-read.", self.slotIndex, hex(status))
                    time.sleep(2)
                    continue
                else:
                    #print("Cassette status:", self.index, hex(status))
                    break;
                    
            #if status != DEVICE_STATE_CASSETTE_POLLED and status in CASSETTE_STATUS:
            if status == DEVICE_STATE_CASSETTE_VALID:
                i2cInstant.write_cmd_arg(I2C_MEM_ACK, status)
                print("Write back ACK")
                
            return status,qrCode
        except Exception as err:
            print("CassettePollingException: ", err)
            return DEVICE_STATE_SUBSYS_EXCEPTION, None
        
    def getQr(self):
        currentMode=getDetectionMode()
        if self.prevMode!=None and self.prevMode!=currentMode:
            print('mode changed')
            self.stopTakePhotoProcedure()
        self.prevMode=currentMode
        if currentMode == CASSETTE_DETECTION_MODE_AUTO:
            return self.autoQr()
        return self.manualQr()
    

##self.notifyQue.put([self.slotNo, int(parsing[RSLT][RCODE]), self.cassetteId, parsing[RSLT][MSSG], recordId[self.slotNo]])
    def deviceDeal(self):  # return [device_slotIndex, state, QRcode, message]
        if self.camera == INVALID_DEVICE_INDEX:
            self.notify([self.slotIndex, DEVICE_STATE_CAMERA_ERROR, '', 'Camera error'])
            return 
        if self.i2c == INVALID_DEVICE_INDEX:
            self.notify([self.slotIndex, DEVICE_STATE_I2C_ERROR, '', 'i2c error'])
            return
        status,qr_code =self.getQr();
        if(status == DEVICE_STATE_CASSETTE_POLLED):
            self.notify( [self.slotIndex, DEVICE_STATE_CASSETTE_POLLED, '', 'no change'])
        elif(status == DEVICE_STATE_CASSETTE_VALID):
            if not main_paras.signedIn():
                main_paras.queueForGui.put([SIGN_IN_FIRST_INDEX,'','',''])
            else:
                self.startTakePhotoProcedure(qr_code,self.qCom)
        elif(status == DEVICE_STATE_CASSETTE_QR):
#             if self.slotIndex == 0:
#                 print('manual waiting qr')
            pass            
        else:
            if (not main_paras.signedIn()) and status != DEVICE_STATE_CASSETTE_EMPTY:
                main_paras.queueForGui.put([SIGN_IN_FIRST_INDEX,'','',''])
            else:
                self.stopTakePhotoProcedure()
                self.notify([self.slotIndex, status, '','Cassette error'])
            
    def periodPoll(self):
        #if self.slotIndex == 0:
        #print("Period poll", time.strftime('%Y%m%d%H%M%S'))
        if self.running:
            self.deviceDeal()
            threading.Timer(DEVICE_POLLING_TIME, self.periodPoll).start()
        else:
            print('periodPoll stop', self.slotIndex)
            
        
    def cameraTest(self):
        photoFile=takePhoto(self.camera, "cameraTest"+'_'+str(self.slotIndex))
        
if __name__ == "__main__":
    import queue
    from main_paras import setDetectionMode
    
    setDetectionMode(CASSETTE_DETECTION_MODE_MANUAL)

    qForGui=queue.Queue()
    qForCom=queue.Queue()
    deviceQue=queue.Queue()
    polling_0= CassettePolling(0, 80, 0, qForGui, qForCom,deviceQue)
    polling_2= CassettePolling(1, 81, 2, qForGui, qForCom,deviceQue)
    polling_4= CassettePolling(2, 82, 4, qForGui, qForCom,deviceQue)
    polling_6= CassettePolling(3, 83, 6, qForGui, qForCom,deviceQue)
    polling_8= CassettePolling(4, 84, 8, qForGui, qForCom,deviceQue)
    polling_0.start()
    polling_2.start()
    polling_4.start()
    polling_6.start()
    polling_8.start()
    
        
