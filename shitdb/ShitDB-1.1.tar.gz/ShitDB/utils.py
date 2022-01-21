import json
from .errors import *


class Utils:
    def to_json(self,file_path,new_json,*,indent=4):
        with open(file_path,"r") as f:
            old = json.load(f)
        old.update(new_json) # became new!
        with open(file_path,"w") as f:
            json.dump(old,file_path,indent=indent)
        return old



    def to_file(self,file_path,con,*,mode="w"):
        if mode=="r":
            raise BadArgs("MODES CAN EITHER BE: w or a, Not r!")
        with open(file_path,mode) as f:
            f.write(con)
        return con



    def load_local_json(self,file_path):
        with open(file_path,"r") as f:
            con = json.load(f)
        return con


    def load_local_file(self,file_path,*,eval_output=False):
        with open(file_path,"r") as f:
            con = str(f.read())
        if eval_output is True:
            return eval(con)
        return con
