import os
import json
import sys
from tqdm import tqdm
import random
import string
class dbc:
    """
    class initialization function
    VL = Version Local
    GMK = global maintaince key
    it is the local version system
    """
    _VERSION  = "0.1.1"
    _GMK = "VL@__LOCAL__"
    _JSON = {
        "version" : _VERSION,
        "gmk" : _GMK,
        "key" : "auto generated ID",
        
    }
class db(dbc):
    """
    IT is local rootoi database managed system
    which works with the NOSQL Databases
    VL = Version Local
    GMK = global maintaince key
    it is the local version system
    """
    def __init__(self,db:str):
        self._dbname = db
        self._db_file_name = f'{self._dbname}.rootoidb'
        self._VERSION  = "0.1.1"
        self._GMK = "VL@__LOCAL__",
        self._ID_KEY = ""
        self.FILE_JSON = {
            "version" : self._VERSION,
            "gmk" : self._GMK,
            "key": self._id_control()
        }
        if(os.path.isfile(self._db_file_name)):
            raise FileExistsError
        else:
            self.dir = os.getcwd() + "\\" + self._dbname
            os.mkdir(self.dir)
            print("[__PROCESS__] designing Project  ")
            for i in tqdm(range(100)):
                pass
            with open(self.dir + "\\"+self._db_file_name,"w") as self._dbfile:
                pass
            for i in tqdm(range(100)):
                pass
            with open(self.dir +"\\" +self._dbname +".json","w") as self._JSON:
                self._JSON.write(json.dumps(self.FILE_JSON,indent=4))
            
            print("[__PROCESS__] designed Project")
            print("Happy Coding !")
    def _id_control(self):
        for i in range(20):
            self._ID_KEY += random.choice(list(string.ascii_lowercase + string.ascii_uppercase+string.digits))
        return self._ID_KEY