import json
import os
import requests
import threading
import time
import sys
import queue

from define import *

from main_paras import api_result_que
class SignIn(threading.Thread):
    def __init__(self, *args):             # self, imageFile, image-identifier, queue
        threading.Thread.__init__(self)
        self.notifyQue = args[0]
        self.user = args[1]
        self.password = args[2]
#qForGui format: [device_index, retCode, QRcode, message]
    def run(self):
        excReason=''
        api_result_que.clear()
        for i in range(API_RETRY_TIME):
            try:
                service = "/signinlookspot"
                url = baseUrl + service
                payload = json.dumps({
#                   "userid": "feng.gao@laipac.com",
#                   "password": "123456"
                  "userid": self.user,
                  "password": self.password
                })
                
                
                headers = {
                  'Authorization': 'Basic bGFpcGFjOmxhaXBhY3dz',
                  'Content-Type': 'application/json'
                }
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
                parsing=json.loads(response.text)
                if parsing[CODE] == RESPONSE_SUCCESS:
                    self.notifyQue.put( [NON_SLOT_INDEX, SIGN_IN_SUCCESS, parsing[RSLT][TKEN], ''] )
                    api_result_que.put( [NON_SLOT_INDEX, SIGN_IN_SUCCESS, parsing[RSLT][TKEN], ''] )
                else:
                    self.notifyQue.put( [NON_SLOT_INDEX, SIGN_IN_FAIL,  parsing[CODE], parsing[DESC]] )
                    api_result_que.put( [NON_SLOT_INDEX, SIGN_IN_FAIL,  parsing[CODE], parsing[DESC]] )
                return
            except Exception as e:
                excReason = "signInException"
                print(e)
            time.sleep(API_RETRY_SLEEP)
            
        else:
            self.notifyQue.put( [NON_SLOT_INDEX, SIGN_IN_FAIL,  excReason, ''] )
            api_result_que.put( [NON_SLOT_INDEX, SIGN_IN_FAIL,  excReason, ''] )
            
def signIn_test():
    notifyQue=queue.Queue()
    signIn=SignIn(notifyQue)
    signIn.start()
    
    while True:
        notify = notifyQue.get()
        print(notify)
        notifyQue.task_done()
        time.sleep(0.1)
        if not signIn.is_alive():
            break;
    print("sign in done")
    

if __name__ == "__main__":
    signIn_test()    
