import json
import os
import requests
import threading
import time
import sys
import queue
#sys.path.append('/home/pi/gxf/python/spotii')
#sys.path.append('/home/pi/gxf/python/spotii/test_chip_handler')

from communication.send_result import SendResult
from define import *
import main_paras



recordId=[None,None,None,None,None]

class WebApi(threading.Thread):
    def __init__(self, *args):             # self, imageFile, image-identifier, queue
        threading.Thread.__init__(self)
        self.imageFile = args[0]
        self.notifyQue = args[1]
        self.passToken = args[2]
        self.address   = args[3]

        
        
        self.fileName   = self.imageFile.split('/')[-1]
        print(self.fileName)
        keyList         = self.fileName.split('_')
        self.cassetteId = keyList[0]
        self.slotNo     = int(keyList[1])
        self.photoIndex = int(keyList[2])
        self.timeStamp  = int(keyList[3])

#qForGui format: [device_index, retCode, QRcode, message]
        
    def addTest(self):
        profile = main_paras.info.getProfile(main_paras.sign_in_user)
        
        service = "/ctestlookspot/addtest"
        url  = baseUrl+service
        if main_paras.info.getCurrentLanguage() == 'Japanese':
            local_date = time.strftime("%Y/%m/%d",time.localtime(self.timeStamp))
        else:
            local_date = time.strftime("%d/%m/%Y",time.localtime(self.timeStamp))
        payload = json.dumps({
          "passtoken": self.passToken,
          "testid": self.cassetteId,
          "site": profile['provider'],
          "place": profile['place'],
          "city": profile['city'],
          "country": profile['country'],
          "timestamp": str(self.timeStamp)+'000',
          "mode": main_paras.info.getTestMode(),
          "localdate": local_date,
          "localtime": time.strftime("%H:%M:%S",time.localtime(self.timeStamp)),
          "readerserial": main_paras.serial
        })
        headers = {
          'Authorization': 'Basic bGFpcGFjOmxhaXBhY3dz',
          'Content-Type': 'application/json'
        }
        print('addTest')
        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)
        
        
#         service = "/ctestlookspot/addtest?"
#         keys = "&testid="+self.cassetteId+ "&place="+self.address[0]+ "&city="+self.address[1]+ "&country="+self.address[2]+"&timestamp="+\
#         str(self.timeStamp)+'000'+"&mode=speed"+\
#         "&localdate="+time.strftime("%d/%m/%Y",time.localtime(self.timeStamp))+\
#         "&localtime="+time.strftime("%H:%M:%S",time.localtime(self.timeStamp))+\
#         "&readerserial="+SERIAL_NO
#         url = baseUrl+service+self.client+keys
#         #print("addtest",url)
#         payload  = {}
#         headers  = {}
#         response = requests.request("POST", url, headers=headers, data=payload)
        
        parsing=json.loads(response.text)
        if parsing[CODE] == RESPONSE_SUCCESS:
            return parsing[RSLT][RCID]
        return None
        

    def uploadImage(self):
        if self.photoIndex == 0:
            imageIndex=self.photoIndex
        else:
            imageIndex=self.photoIndex-1

        service = "/testimagelookspot/upload"
        url = baseUrl + service
        payload={'passtoken': self.passToken,
        'lstestrecordid': str(recordId[self.slotNo]),
        'lstestid': self.cassetteId,
        'imageindex': str(imageIndex)}
        files=[
          ('uploadimage',(self.fileName,open(self.imageFile,'rb'),'image/jpeg'))
        ]
        headers = {
          'Authorization': 'Basic bGFpcGFjOmxhaXBhY3dz'
        }
        
        print('uploadImage')
        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload, files=files)
        
        print(response.text)
        
        
        
        
        
#         service = "/testimagelookspot/upload?"
#         if self.photoIndex == 0:
#             imageIndex=self.photoIndex
#         else:
#             imageIndex=self.photoIndex-1
#         keys = "&lstestrecordid="+ str(recordId[self.slotNo])+"&lstestid="+self.cassetteId+"&imageindex="+ str(imageIndex)
#         url = baseUrl+service+self.client+keys
#         #url = "https://www.locationnow.com/lnservices/ws/testimagelookspot/upload?client=laipac&signature=laipacws&passtoken=1b9f3867298b394a&lstestrecordid=6118&lstestid=La0000888&imageindex=0"
#         payload={}
#         files=[
#           ('uploadimage',(self.fileName,open(self.imageFile,'rb'),'image/jpeg'))
#         ]
#         headers = {}
#         response = requests.request("POST", url, headers=headers, data=payload, files=files)        
#         print(response.text)
        
        parsing=json.loads(response.text)
        if parsing[CODE] == RESPONSE_SUCCESS:                            
            self.notifyQue.put([self.slotNo, int(parsing[RSLT][RCODE]), self.cassetteId, parsing[RSLT][MSSG], recordId[self.slotNo]])
        try:
            #pass
            os.remove(self.imageFile)
        except Exception as e:
            print(e)
        return None

    def run(self):
        if recordId[self.slotNo] == None or self.photoIndex == 0:
            recordId[self.slotNo]=self.addTest()
                        
        if recordId[self.slotNo] == None:
            self.notifyQue.put([self.slotNo, -1, "Retry", "Add test Fail"])
            return
        
        print('web api run',recordId)
        self.uploadImage()

WIN_IMG_PATH = 'C:/gxf/document/spotII/main_box/ui_design/image/send_buffer/'
def sendToApi(imageFile, notifyQue, passToken, address): # uploading imagefile name and test result share same queue, file name is string, test result is a list.
    if type(imageFile) ==str:
        if sys.platform == 'win32':
            webApi=WebApi(WIN_IMG_PATH+imageFile, notifyQue, passToken, address)            
        else:
            webApi=WebApi(IMG_PATH+imageFile, notifyQue, passToken, address)
        webApi.start()
    else:
        sendResult=SendResult(imageFile, passToken)
        sendResult.start()
    
def sendToApi_test():
    imageFile = "La0000835_0_0_1615836967_20210315153607.jpg"
    notifyQue=queue.Queue()
    passToken = "111111111111"
    sendToApi(imageFile, notifyQue, passToken, ADDRESS)
    
def time_test():
    print(time.gmtime())
    t=time.time()
    print(time.gmtime(t))
    print(time.strftime("%b %d %Y %H:%M:%S", time.gmtime(t)))
    print(time.strftime("%b %d %Y %H:%M:%S", time.localtime(t)))
    print(time.strftime("%d/%m/%Y", time.localtime(t)))
    print(time.strftime("%H:%M:%S", time.localtime(t)))

if __name__ == "__main__":
    #sendToApi_test()
    time_test()
