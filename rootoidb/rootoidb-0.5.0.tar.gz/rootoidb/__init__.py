from json import JSONDecodeError
import os 
import pathlib
import json
class User:
    """
    NOTE : Preferable Not to use as it will automatically done in CRUD_ROOTOI CLASS
    use : it helps in authetication of the file
    """
    def __init__(self,project_path ,  project_name , key):
        self.project_file = project_path +"\\"+project_name+ ".rootoidb"
        self._json = project_path +"\\"+project_name+ ".json"
        self._module_version = ['0.1.1']
        self._auth_key = key
        self._check1 = os.path.isfile(self.project_file)
        self._check2 = os.path.isfile(self._json)
        self._check3 = pathlib.Path(".\\"+self.project_file).is_file()
        self._check4 = pathlib.Path(".\\"+self._json).is_file()
        self.control = ""
        if(self._check1 == True and self._check2 == True):
            try:
                with open(self._json,"r") as file:
                    self._json_auth_data = json.load(file)
                    self._json_auth_data_keys = self._json_auth_data.keys()
                    if(('version'in self._json_auth_data_keys) and ('gmk' in self._json_auth_data_keys) and ('key'in self._json_auth_data_keys) ):
                        if((self._json_auth_data['version'] == self._module_version[0]) and (self._json_auth_data['gmk'][0] == 'VL@__LOCAL__') and (self._json_auth_data['key'] == self._auth_key)):
                            self.control = self._auth_key 
                        else:
                            raise ValueError
                    else:
                        raise JSONDecodeError
            except Exception as e:
                raise e
        elif(self._check3 == True and self._check4 == True):
            try:
                with open(self._json,"r") as file:
                    self._json_auth_data = json.load(file)
                    self._json_auth_data_keys = self._json_auth_data.keys()
                    if(('version'in self._json_auth_data_keys) and ('gmk' in self._json_auth_data_keys) and ('key'in self._json_auth_data_keys) ):
                        if((self._json_auth_data['version'] == self._module_version[0]) and (self._json_auth_data['gmk'][0] == 'VL@__LOCAL__') and (self._json_auth_data['key'] == self._auth_key)):
                            self.control = self._auth_key 
                        else:
                            raise ValueError
                    else:
                        raise JSONDecodeError
            except Exception as e:
                raise e
        else:
            raise FileNotFoundError
    def is_verified(self) -> dict:
        try:
            return {"verified":True, "key":self.control,"project":self.project_file,"auth": self._json}
        except Exception as e:
            return {"verified":False}
class RootoiBaseUnverifiedError(Exception):
    def __init__(self,message = "The Rootoi is not verified Please check your key"):
        self.err = message
        super().__init__(self.err)
class RootoiKeyUnverifiedError(Exception):
    def __init__(self,message = "The Rootoi Admin Key is not verified Please check your key"):
        self.err = message
        super().__init__(self.err)
class RootoiDictError(Exception):
    def __init__(self,message = "there should be an dictionary"):
        self.err = message
        super().__init__(self.err)

def _sequel(data):
    _a = ""
    for i in data:
        _a+=str(i) + " "
    return _a
class CRUD_ROOTOI:
    """
    THIS IS THE MAIN CLASS WHERE YOU CAN
    START YOUR PROJECT AND DO CRUD
    OPERATION
    USAGE : EASY TO USE
    KEYWORDS : 
    RD - Rootoi Delete
    """
    def __init__(self,project_path ,  project_name , key,column):
        self.user_auth = User(project_path ,  project_name , key )
        self.user_auth_res = self.user_auth.is_verified()
        self.uik = key
        self.col = column
        if(self.user_auth_res['verified'] == True):
            with open(self.user_auth_res['auth'],"r") as self._jf:
                self._jslo = json.load(self._jf)
                if(self._jslo['key'] == self.uik):
                    if(type(column) == int):
                        self._current_operation = True
                    else:
                        raise ValueError("Column must be an integer")
                else:
                    raise RootoiKeyUnverifiedError
        else:
            raise RootoiBaseUnverifiedError
    def write(self, data):
        if(type(data) == list):
            self.pro = self.user_auth_res['project']
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
        self.proo = self.user_auth_res['project']
        self.retrive = []
        with open(self.proo,"r") as self.rf:
            self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
            return self.newstrr
    def read_by_row(self,row):
        if(row > 0):
            self.proo = self.user_auth_res['project']
            self.retrive = []
            with open(self.proo,"r") as self.rf:
                self.newstrr = [i.strip().split(" ") for i in self.rf.readlines()]
                return self.newstrr[row-1]
        else:
            raise ValueError("The Value must be greater than 0")
    def read_by_column(self,col):
        if(col > 0):
            self.proo = self.user_auth_res['project']
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
            self.proo = self.user_auth_res['project']
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
            self.proo = self.user_auth_res['project']
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
            self.proo = self.user_auth_res['project']
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
            self.proo = self.user_auth_res['project']
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
