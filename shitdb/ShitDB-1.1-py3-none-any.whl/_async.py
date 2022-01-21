from .core import DB
import json
from .errors import *



class AsyncDB:
    """
    This ain't actually async.
    It just segregates "sync" requests to different threads.
    The real AsyncDB with aiohttp and asyncio is yet to be made...better help mee
    """
    def __init__(self,github_token:str,database_repo:str,author:tuple,branch:str = None):
        self.db = DB(github_token,database_repo,author,branch)
        self.repo = self.db.repo
        self.branch = self.db.branch
        self.github = self.db.github
        self.key = self.db.key
        self.author = self.db.author



    async def push_remote_data(self,content,file_path,*,msg="ShitDB",branch = None):
        if branch is None:
            try:
                self.repo.create_file(file_path,msg,str(content))
            except:
                sha = self.repo.get_contents(file_path,ref=self.branch).sha
                self.repo.update_file(file_path,msg,str(content),sha,branch=self.branch)
            return content
        try:
            self.repo.create_file(file_path,msg,str(content),branch=branch)
        except:
            sha = self.repo.get_contents(file_path,ref=branch).sha
            self.repo.update_file(file_path,msg,str(content),sha,branch=branch)
        return content





    async def load_remote_data(self,file_path,*,eval_output=False,branch=None):
        if branch is None:
            con = self.repo.get_contents(file_path,ref=self.branch).decoded_content.decode("utf-8")
        else:
            con = self.repo.get_contents(file_path,ref=branch).decoded_content.decode("utf-8")
        if eval_output is True:
            return eval(con)
        return con





    async def to_json(self,file_path,new_json,*,indent=4):
        with open(file_path,"r") as f:
            old = json.load(f)
        old.update(new_json) # became new!
        with open(file_path,"w") as f:
            json.dump(old,file_path,indent=indent)
        return old



    async def to_file(self,file_path,con,*,mode="w"):
        if mode=="r":raise BadArgs("MODES CAN EITHER BE: w or a, Not r!")
        with open(file_path,mode) as f:
            f.write(con)
        return con



    async def load_local_json(self,file_path):
        with open(file_path,"r") as f:
            con = json.load(f)
        return con


    async def load_local_file(self,file_path,*,eval_output=False):
        with open(file_path,"r") as f:
            con = str(f.read())
        if eval_output is True:
            return eval(con)
        return con




    async def sync(self,file_path,prefer="remote",*,dry=False):
        prefer=prefer.lower()
        fp=file_path
        j = False
        if fp.endswith(".json"):
            j = True
        dry=bool(dry)
        allowed=['remote','local']
        if prefer not in allowed:
            raise BadArgs(f"Args must be {', '.join(allowed)}; not \"{prefer}\"")
        if dry is True:
            if j:
                return self.load_local_json(fp)==self.load_remote_data(fp,True)
            return self.load_local_file(fp)==self.load_remote_data(fp)

        if prefer=="remote":
            if j:
                self.to_json(self.load_remote_data(fp,True),fp)
                return self.load_local_json(fp)==self.load_remote_data(fp,True), "Overrided LOCAL data"
            self.to_file(self.load_remote_data(fp),fp)
            return self.load_local_file(fp)==self.load_remote_data(fp), "Overrided LOCAL data"

        elif prefer=="local":
            if j:
                if self.load_local_json(fp)==self.load_remote_data(fp,True):
                    return True,"Already Synced!!"
            else:
                if self.load_local_file(fp)==self.load_remote_data(fp):
                    return True,"Already Synced!!"
            self.push_remote_data(self.load_local_file(fp))
            return self.load_local_file(fp)==self.load_remote_data(fp), "Overrided REMOTE data"








