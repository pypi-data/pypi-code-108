import json
import os
import requests
import threading
import time
import sys
import queue

from define import *

from main_paras import api_result_que
class ChgPsw(threading.Thread):
    def __init__(self, *args):
        threading.Thread.__init__(self)
        self.passToken   = args[0]
        self.password   = args[1]
        self.newPassword  = args[2]
    def run(self):
        excReason=''
        api_result_que.clear()
        for i in range(API_RETRY_TIME):
            try:
                service = "/changepwdlookspot"
                url = baseUrl + service
                payload = json.dumps({
                  "passtoken": self.passToken,
                  "oldpassword": self.password,
                  "newpassword":self.newPassword,
                })
                headers = {
                  'Authorization': 'Basic bGFpcGFjOmxhaXBhY3dz',
                  'Content-Type': 'application/json'
                }
                print(payload)
                response = requests.request("POST", url, headers=headers, data=payload)
                print(response.text)
                parsing=json.loads(response.text)
                if parsing[CODE] == RESPONSE_SUCCESS:
                    api_result_que.put( [NON_SLOT_INDEX, API_RESPONSE_SUCCESS,  parsing[CODE], parsing[RSLT]] )
                else:
                    api_result_que.put( [NON_SLOT_INDEX, API_RESPONSE_FAIL,  parsing[CODE], parsing[RSLT]] )
                return
            except Exception as e:
                excReason = "signUpException"
                print('exception ChgPsw', e)
            time.sleep(API_RETRY_SLEEP)
            
        else:
            print('ChgPsw timeout')
            api_result_que.put( [NON_SLOT_INDEX, API_RESPONSE_FAIL,  excReason, 'time out'] )
            
def test():
    notifyQue=queue.Queue()
    signIn=SignUp(notifyQue)
    signIn.start()
    
    while True:
        notify = notifyQue.get()
        print(notify)
        notifyQue.task_done()
        time.sleep(0.1)
        if not SignUp.is_alive():
            break;
    print("sign up done")
    

if __name__ == "__main__":
    test()    
