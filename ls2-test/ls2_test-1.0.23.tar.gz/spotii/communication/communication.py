import threading
import time
import queue
import sys

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from communication.ln_web import sendToApi
from communication.sign_in import SignIn
from communication.sign_up import SignUp
from communication.change_password import ChgPsw
from communication.forgot_password import ForgotPassword
from communication.test_report_email import TestReportEmail
from communication.get_report_email import GetReportEmail
from communication.get_report import GetReport
from define import *
import main_paras
    
class CommunicationThread (threading.Thread):
    def __init__(self, threadID, name, qForCom, qForResult):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.qForCom=qForCom
        self.qForResult=qForResult
        self.notifyQue=queue.Queue()
        self.passToken=''
        
    def signIn(self, user, password):        
        signIn=SignIn(self.notifyQue, user, password)
        signIn.start()
        notify = self.notifyQue.get()
        if notify[1] == SIGN_IN_SUCCESS:
            self.passToken = notify[2]
#        print(notify)
        self.notifyQue.task_done()
        signIn.join()
        print("sign in done")

    def signUp(self, user, password, firstName, lastName):        
        sign_up=SignUp(user, password, firstName, lastName)
        sign_up.start()
        sign_up.join()
        print("sign up done")

    def chgPsw(self, token, password, newPassword):        
        chg_psw=ChgPsw(token, password, newPassword)
        chg_psw.start()
        chg_psw.join()
        print("change password done")

    def forgotPsw(self, email):        
        forgot_psw=ForgotPassword( email)
        forgot_psw.start()
        forgot_psw.join()
        print("forgot password done")
        
    def testReportEmail(self, token, email_1, email_2):        
        test_report_email=TestReportEmail(token, email_1, email_2)
        test_report_email.start()
        test_report_email.join()
        print("test report email set done")

    def getReportEmail(self, token):        
        get_report_email=GetReportEmail(token)
        get_report_email.start()
        get_report_email.join()
        print("get report email done")

    def getReport(self, token):        
        get_report=GetReport(token)
        get_report.start()
        get_report.join()
        print("get report request sent")

    def webApi(self):
        while True:
            image=self.qForCom.get()
            print('in communication',image)
            if image == CLOSE_NOW:
                self.qForCom.task_done()
                break;

            if not main_paras.isWifiOk():
                print('wifi problem')
                #main_paras.guiNotify(CHECK_NETWORK_INDEX)
                main_paras.api_result_que.put(None)
                self.qForCom.task_done()
                continue;
            
            if type(image) ==list:
#                print(image)
                if image[0] == SIGN_IN:    #[SIGN_IN, user, password]
                    self.signIn(image[1],image[2])
                    continue
                elif image[0] == SIGN_UP:    #[SIGN_UP, user, password, firstName, lastName]
                    self.signUp(image[1], image[2], image[3], image[4])
                    continue
                elif image[0] == CHG_PSW:    #[CHG_PSW, password, new_password]
                    self.chgPsw(main_paras.sign_in_token, image[1], image[2])
                    continue
                elif image[0] == FORGOT_PSW:    #[FORGOT_PSW, email]
                    self.forgotPsw(image[1])
                    continue
                elif image[0] == TEST_REPORT_EMAIL:    #[TEST_REPORT, email_1, email_2]
                    self.testReportEmail(main_paras.sign_in_token, image[1], image[2])
                    continue
                elif image[0] == GET_REPORT_EMAIL:    #[GET_REPORT_EMAIL, passtoken]
                    self.getReportEmail(main_paras.sign_in_token)
                    continue
                elif image[0] == GET_REPORT:    #[GET_REPORT, passtoken]
                    self.getReport(main_paras.sign_in_token)
                    continue
            sendToApi(image, self.qForResult, self.passToken, [main_paras.test_place, main_paras.test_city, main_paras.test_country])
            self.qForCom.task_done()
        
    def run(self):
        super().run()
        print("communication thread start.")
        #self.aiServer()
        self.webApi()
  
#################### Test ####################
def com_test():
    qForCom=queue.Queue()
    qForResult = queue.Queue()
    com=CommunicationThread(3,"communication",qForCom, qForResult)
    com.start()
    
    time.sleep(2)
    

if __name__ == "__main__":
    com_test()   
