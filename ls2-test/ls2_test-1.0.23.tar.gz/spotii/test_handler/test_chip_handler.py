import sys
import subprocess
import threading
import time
from datetime import datetime,timezone
import queue

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from test_handler.i2c_lib import i2c_device
from test_handler.cassette_polling import CassettePolling
from define import *
import main_paras
from on_off.mainboard_pio import hub_reset
# from smbus import SMBus
# import sys
# sys.path.append('/home/pi/gxf/python/spotii')
# sys.path.append('/home/pi/gxf/python/spotii/test_chip_handler')
# import subprocess
# import queue
# 
# from mythread import MyThread
# import time
# import threading
# from i2c_lib import i2c_device
# from takePhoto import takePhoto
# from datetime import datetime,timezone
# from define import *

 

I2C                 =0
CAMERA              =1
# part of "v4l2-ctl --list-devices" parsing sample sentence
# USB 2.0M Camera: USB 2.0M Camer (usb-0000:01:00.0-1.1.1):
#     /dev/video0   <------ "0" is second target        ^
#     /dev/video1                                       |________"1" is first target 

def usbCameraFinder(deviceInfo):
    detail=deviceInfo.split('\n\t')
    if 'video' in detail[1]:
        return [ord(detail[0].split(')')[0][-1])-ord('0') -1 , ord(detail[1][-1])-ord('0')]
    return None

#    usbList=subprocess.check_output(['v4l2-ctl','--list-devices']).decode("utf-8").split('usb-0000:01:00.0-1.1.')
def cameraMap(cMap):
    try:
        usbList=subprocess.check_output(['v4l2-ctl','--list-devices']).decode("utf-8").split('(usb-0000:')
        
    except Exception as e:
        print("cameraMap exception:",e)
        return False
    
    for phase in usbList[1:]:
#        print (phase)
        cameraList=usbCameraFinder(phase)
        print(cameraList)
        if(cameraList):
            cMap[cameraList[0]][1]=cameraList[1]
    return True

def cameraClr(cMap):
    for each in cMap:
        each[CAMERA]=INVALID_DEVICE_INDEX

def i2cMap(cMap):
    
    phase=subprocess.check_output(['i2cdetect','-y','5']).decode("utf-8").split('50: ')
    i2cList=phase[1].split(' ')
    index = 0
    for each in cMap:
        if i2cList[index] == '--' or int(i2cList[index],16) != each[I2C] :
            each[I2C] = INVALID_DEVICE_INDEX
        index+=1



class TestChipHandlerThread (threading.Thread):
    def __init__(self, threadID, name, qForCom, qForGui, qForResult):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qCom = qForCom
        self.qGui = qForGui
        self.qForResult=qForResult
        self.cassettePolling=[None]*5
        self.i2c=[]
        self.cmrMap=[]
        self.initDone = True

        self.deviceQue=[]
        self.checkingResult=[]  # [[0,0,0,0,0,0,0], ..., [0,0,0,0,0,0,0]] total (I2C_PORT)
                    #
        self.startCheck=[]
        for i in range(I2C_PORT):
            self.deviceQue.append(queue.Queue())
            self.checkingResult.append([])
            self.startCheck.append(False)

# RESULT_SLOT_NUMBER 0
# RESULT_ERROR_CODE  1
# RESULT_CASSETTE_ID 2
# RESULT_TEXT        3
    def checkingStop(self, slotNumber):
        self.startCheck[slotNumber]=False
        self.deviceQue[slotNumber].put(PHOTO_TAKING_STOP)
        
    def checkingStart(self, slotNumber):
        self.startCheck[slotNumber] = True
        self.checkingResult[slotNumber].clear()

    def resultReport(self, result):
        if Negative_test_result == result[RESULT_ERROR_CODE] or Positive_test_result == result[RESULT_ERROR_CODE]:
            self.qCom.put(result)
        print('put result',result)
        self.qGui.put(result)
        
    def putToResultList(self, result):     #There is nothing for RESULT_CASSETTE_ID if message is from sub thread. message from communication must have something on RESULT_CASSETTE_ID 
        #print('in putToResultList', result)
        if result[RESULT_ERROR_CODE] == DEVICE_STATE_TAKING_PHOTO:
            self.checkingStart(result[RESULT_SLOT_NUMBER])
            self.qGui.put(result)
        elif result[RESULT_ERROR_CODE] == DEVICE_STATE_MANUAL_FLIP:
            #print('manual flip')
            self.qGui.put(result)
        elif result[RESULT_ERROR_CODE] == DEVICE_STATE_MANUAL_INVALID_QR:
            self.qGui.put(result)
        elif result[RESULT_CASSETTE_ID] == '':
            self.qGui.put(result)
        elif self.startCheck[result[RESULT_SLOT_NUMBER]] == True:
            self.resultReport(result)
            self.checkingStop(result[RESULT_SLOT_NUMBER])
            return;
            
#             if main_paras.info.getTestMode()==TEST_MODE_SPEED:
#                 self.resultReport(result)
#                 self.checkingStop(result[RESULT_SLOT_NUMBER])
#                 return;
#             
#             if Negative_test_result == result[RESULT_ERROR_CODE] or Control_area_not_found == result[RESULT_ERROR_CODE] :                                
#                 self.checkingResult[result[RESULT_SLOT_NUMBER]].append(result)
#                 if len(self.checkingResult[result[RESULT_SLOT_NUMBER]]) == len(PHOTO_TAKING_GAPS):
#                     self.resultReport(result)
#                     self.checkingStop(result[RESULT_SLOT_NUMBER])
#             elif Positive_test_result == result[RESULT_ERROR_CODE]: 
#                 for each in self.checkingResult[result[RESULT_SLOT_NUMBER]]:
#                     if Positive_test_result == each[RESULT_ERROR_CODE]: ## report if get 2 poisitve result
#                         self.resultReport(result)
#                         self.checkingStop(result[RESULT_SLOT_NUMBER])
#                         break;                   
#                 self.checkingResult[result[RESULT_SLOT_NUMBER]].append(result)
#             else:
#                 self.checkingStop(result[RESULT_SLOT_NUMBER])
#                 self.resultReport(result)
                
    def run (self):
        super().run()
        print('test monitor run...')
        
        for addr in I2C_DEVICE:
            self.cmrMap.append([addr, INVALID_DEVICE_INDEX])            
        for i in range(3):
            if cameraMap(self.cmrMap)==True:
                break;
            self.qGui.put([NON_SLOT_INDEX, -1 , 'Critical error', 'Critical error'])
            hub_reset.off()
            time.sleep(0.5)
            hub_reset.on()
            time.sleep(4)           
        else:
            self.initDone =False
             
        print(self.cmrMap)
        i2cMap(self.cmrMap)
        print(self.cmrMap)
        
        if self.initDone == False:
            self.qGui.put([NON_SLOT_INDEX, -1 , 'Critical error', 'Critical error'])
            while True:
                None

        for i in range(5):
            self.cassettePolling[i]=CassettePolling(i, self.cmrMap[i][I2C], self.cmrMap[i][CAMERA], self.qForResult, self.qCom, self.deviceQue[i])
            self.cassettePolling[i].start()
        while True:
            result=self.qForResult.get() #[0, 1, 'La0012684', 'Negative']
            
            if result == CLOSE_NOW:
                for i in range(5):
                    self.cassettePolling[i].notify(CLOSE_NOW)
                #for i in range(5):
                self.cassettePolling[0].join()
#                 self.cassettePolling[1].join()
#                 self.cassettePolling[2].join()
#                 self.cassettePolling[3].join()
#                 self.cassettePolling[4].join()
                print('got CLOSE_NOW')
                break;
            else:
                self.putToResultList(result)
            self.qForResult.task_done()
            
def i2cTest():
    data=[1,2,3]
    i2cInstant= i2c_device(0x52,I2C_PORT)
    #receiving=i2cInstant.read_block_data(4,6)
    #print(receiving)
    
#     i2cInstant.write_cmd_arg(I2C_MEM_LED_1, 1)
#     time.sleep(0.005)
    i2cInstant.write_cmd_arg(I2C_MEM_LED_2, 0)
    time.sleep(0.005)
#     i2cInstant.write_cmd_arg(I2C_MEM_UV, 1)

#    i2cInstant.write_cmd_arg(I2C_MEM_FORCE_READ, 1)


#     receiving=i2cInstant.read_data(0)
#     print(''.join('{:02x}'.format(receiving)))
# 
    receiving=i2cInstant.read_data(0)
    print(''.join('{:02x}'.format(receiving)))

    receiving=i2cInstant.read_block_data(I2C_MEM_ID, 12)
    print(''.join('{:02x}'.format(x) for x in receiving))

    receiving=i2cInstant.read_block_data(I2C_MEM_UID, 12)
    print(''.join('{:02x}'.format(x) for x in receiving))
    
    
#     receiving=i2cInstant.read_block_data(I2C_COMMAND_ID, 12)
#     print(''.join('{:02x}'.format(x) for x in receiving))
# 
#     receiving=i2cInstant.read_block_data(I2C_COMMAND_UID, 12)
#     print(''.join('{:02x}'.format(x) for x in receiving))

#    i2cInstant.write_cmd_arg(I2C_COMMAND_SET_BLOCK_NO,6)
#    i2cInstant.write_cmd(I2C_COMMAND_SYSTEM_RESET)
# 
    
def cameraMapTest():
    hub_reset.off()
    time.sleep(0.5)
    hub_reset.on()
    time.sleep(4)
    cmrMap=[]
    for addr in I2C_DEVICE:
        cmrMap.append([addr, INVALID_DEVICE_INDEX])
    
    cameraMap(cmrMap)
    print(cmrMap)
    i2cMap(cmrMap)
    print(cmrMap)

def hubTest(): #for hum SMBUS mode, must set SEL2-SEL0 to 001
#     data=[1,2,3]
#     i2cInstant= i2c_device(0x2C,I2C_PORT)
#     time.sleep(1)
#     receiving=i2cInstant.read_block_data_smbus(0)
#     print(receiving)

        try:
            bus=SMBus(5)
            receiving=bus.read_block_data(0x2C,0)
            print(receiving)
        except:
            print("read error")
            
def threadTest():
    qForGui=queue.Queue()
    qForCom=queue.Queue()
    qForResult=queue.Queue()
    TestMonitor=TestChipHandlerThread(3,"TCH",qForCom, qForGui, qForResult)
    TestMonitor.start()
if __name__ == "__main__":

#    threadTest()
    cameraMapTest()   
#    i2cTest()
#    hubTest();        
        
