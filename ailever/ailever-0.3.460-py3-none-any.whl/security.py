import requests

class SecurityError(Exception):
    pass

class Supervisor:
    def __init__(self):
        self.__token = None
        self.__ailever_verification_code = requests.get('https://raw.githubusercontent.com/ailever/security/master/verification.json').json()["verification code"]
        self.__ailever_sudoer_code = requests.get('https://raw.githubusercontent.com/ailever/security/master/verification.json').json()["sudoer code"]
        verification = input("[AILEVER] Enter ailever verification code : ")
        if self.__ailever_verification_code == verification or self.__ailever_sudoer_code == verification:
            self.__token = verification
        else : raise SecurityError('[AILEVER] Permission denied.')
        from collections import OrderedDict
        self.__users = OrderedDict()
        self.__users['sudo'] = 'ailever'
    
    @property
    def tokenextract(self):           
        return self.__token
 
    @tokenextract.setter
    def tokeninsert(self, value):    
        self.__token = value

    def enroll(self, account, passwd):
        self.__users[account] = passwd

    def members(self):
        return self.__users.keys()
    
    def identify(self, account, passwd):
        if self.__users[account] == passwd:
            return True
        else:
            return False

sudo = Supervisor()
