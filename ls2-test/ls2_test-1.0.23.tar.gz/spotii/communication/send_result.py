import json
import os
import requests
import threading
import time
import sys
import queue
#sys.path.append('/home/pi/gxf/python/spotii')
#sys.path.append('/home/pi/gxf/python/spotii/test_chip_handler')

from define import *

#baseUrl = "https://www.locationnow.com/lnservices/ws"

class SendResult(threading.Thread):
    def __init__(self, *args):             # self, imageFile, image-identifier, queue
        threading.Thread.__init__(self)
        item = args[0]
        #print("send result args 0",item)
        self.cassetteId= item[RESULT_CASSETTE_ID]
        self.slotNo    = item[RESULT_SLOT_NUMBER]
        self.recordId  = item[RESULT_RECORD_ID]
        if item[RESULT_ERROR_CODE] == Positive_test_result:
            self.result = "Positive"
        else:
            self.result = "Negative"
        
        self.passToken = args[1]
#qForGui format: [device_index, retCode, QRcode, message]
    def run(self):
        service = "/ctestlookspot/saveresult"
        url = baseUrl + service
        payload = json.dumps({
          "passtoken": self.passToken,
          "testid": self.cassetteId,
          "lstestrecordid": self.recordId,
          "result": self.result,
          "slots": str(self.slotNo)
        })
        headers = {
          'Authorization': 'Basic bGFpcGFjOmxhaXBhY3dz',
          'Content-Type': 'application/json'
        }
#        print('save result:', payload)
        print('save result:', payload)
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)
        
        
        
#         service = "/ctestlookspot/saveresult?"
#         
#         keys = "&testid="+self.cassetteId +"&lstestrecordid="+self.recordId+"&result="+self.result +"&slots="+str(self.slotNo)        
#         url = baseUrl+service+self.client+keys
#         #url = "https://www.locationnow.com/lnservices/ws/ctestlookspot/saveresult?client=laipac&signature=laipacws&passtoken=1b9f3867298b394a&testid=La0000888&result=Positive&slots=0"
#         #print(url)
#         payload={}
#         headers = {}
#         response = requests.request("POST", url, headers=headers, data=payload)
#         print(response.text)
        
def sendResult_test():
    result = [0, 0, "La0000001", "NNN"]
    sendResult=SendResult(result, "client=laipac&signature=laipacws&passtoken=1b9f3867298b394a")
    sendResult.start()
    

if __name__ == "__main__":
    sendResult_test()    
