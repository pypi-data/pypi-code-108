import os
from json import JSONDecodeError
import json
import threading
import rootoidb
from rootoidb import RootoiBaseUnverifiedError  , RootoiKeyUnverifiedError , RootoiDictError , _sequel
class FRDBV_User:
    def __init__(self,project_name, key):
        self.files = [project_name+'.rootoidb',project_name+'.json']
        self._module_version = ['0.1.1']
        self._auth_key = key
        self.c1 , self.c2 = os.path.isfile(self.files[0]) , os.path.isfile(self.files[1])
        if(self.c1 == True and self.c2 == True):
            with open(self.files[1],"r") as file:
                self._json_auth_data = json.load(file)
                self._json_auth_data_keys = self._json_auth_data.keys()
                if(('version'in self._json_auth_data_keys) and ('gmk' in self._json_auth_data_keys) and ('key'in self._json_auth_data_keys) ):
                    if((self._json_auth_data['version'] == self._module_version[0]) and (self._json_auth_data['gmk'][0] == 'VL@__LOCAL__') and (self._json_auth_data['key'] == self._auth_key)):
                        self.control = self._auth_key 
                    else:
                        raise ValueError
                else:
                    raise JSONDecodeError
        else:
            raise FileNotFoundError
    def is_verified(self) -> dict:
        try:
            return {"verified":True, "key":self._auth_key,"project":self.files[0],"auth": self.files[1]}
        except Exception as e:
            return {"verified":False}

class FRDBV:
    """
    This is the Main class which is used to do main operation
    """
    def __init__(self,app):
        self.file = app.config.get("ROOTOIDB_CONFIG_NAME")
        self.col = app.config.get("ROOTOIDB_CONFIG_COL")
        self.key = app.config.get("ROOTOIDB_CONFIG_JSON_KEY")
        self.user = FRDBV_User(self.file,self.key)
        self.verified = self.user.is_verified()
        self.thread = threading.Thread(target=self._veri)
        self.thread.start()
    def _veri(self):
        if(self.verified.get('verified') == True):
            with open(self.verified.get('auth'),"r") as self._jf:
                self._jslo = json.load(self._jf)
                if(self._jslo['key'] == self.key):
                    if(type(self.col) == int):
                        self._current_operation = True
                    else:
                        raise ValueError("Column must be an integer")
                else:
                    raise RootoiKeyUnverifiedError
        else:
            raise RootoiBaseUnverifiedError
    def write(self, data):
        if(type(data) == list):
            self.pro = self.verified.get('project')
            if(self.col == len(data)):
                with open(self.pro , "a") as self.wf:
                    self.strr = ""
                    for i in range(len(data)):
                        self.strr += str(data[i]) + " "
                    self.wf.write(self.strr+"\n")
            else:
                raise ValueError("Column must be Equal")
        else:
            raise ValueError("List datatype Should be used here")
    def read(self):
        self.proo = self.verified.get('project')
        self.retrive = []
        with open(self.proo,"r") as self.rf:
            self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
            return self.newstrr
    def read_by_row(self,row):
        if(row > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
                return self.newstrr[row-1]
        else:
            raise ValueError("The Value must be greater than 0")
    def read_by_column(self,col):
        if(col > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
                self.leni = len(self.newstrr[0])
                self.copi = []
                for i in self.newstrr:
                    self.copi.append(i[col-1])
            return self.copi
        else:
            raise ValueError("The Value must be greater than 0")
    def update(self,row,col,value):
        if(row > 0 or col > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            self.blk = []
            self.neww = ""
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
                self.newstrr[row-1][col-1] = str(value)
            self.blk.append(self.newstrr)
            open(self.proo,"w").close()
            with open(self.proo, "a") as self.uf:
                for i in self.blk[0]:
                    self._ef = _sequel(i)
                    self.uf.write(self._ef+"\n")
        else:
            raise ValueError("The Value must be greater than 0")
    def delete(self, row, col):
        if(row > 0 or col > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            self.blk = []
            self.neww = ""
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
                self.newstrr[row-1][col-1] = "RD"
            self.blk.append(self.newstrr)
            open(self.proo,"w").close()
            with open(self.proo, "a") as self.uf:
                for i in self.blk[0]:
                    self._ef = _sequel(i)
                    self.uf.write(self._ef+"\n")
        else:
            raise ValueError("The Value must be greater than 0")
    def delete_by_row(self, row):
        if(row > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            self.blk = []
            self.neww = ""
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
            self.newstrr.pop(row-1)
            self.blk.append(self.newstrr)
            open(self.proo,"w").close()
            with open(self.proo, "a") as self.uf:
                for i in self.blk[0]:
                    self._ef = _sequel(i)
                    self.uf.write(self._ef+"\n")
        else:
            raise ValueError("The Value must be greater than 0")
    def delete_by_column(self,col):
        if(col > 0):
            self.proo = self.verified.get('project')
            self.retrive = []
            self.blk = []
            self.neww = ""
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
            for i in self.newstrr:
                i.pop(col-1)
                i.insert(col-1,'RD')
                self.retrive.append(i)
            self.blk.append(self.retrive)
            open(self.proo,"w").close()
            with open(self.proo, "a") as self.uf:
                for i in self.blk[0]:
                    self._ef = _sequel(i)
                    self.uf.write(self._ef+"\n")
        else:
            raise ValueError("The Value must be greater than 0")
