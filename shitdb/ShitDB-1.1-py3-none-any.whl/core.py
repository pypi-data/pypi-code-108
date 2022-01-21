import json
from github import *
from .errors import *



class DB:
    def __init__(self,github_token:str,database_repo:str,author:tuple,branch:str = None):
        self.github = Github(github_token)
        self.key = github_token
        self.author = InputGitAuthor(name=author[0],email=author[1])
        self.repo = self.github.get_repo(f"{author[0]}/{database_repo}")
        if branch is None:
            self.branch = self.repo.get_branches()[0].name
        else:
            self.branch = self.repo.get_branch(branch=branch).name


    def push_remote_data(self,content,file_path,*,msg="ShitDB",branch = None):
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



    def load_remote_data(self,file_path,*,eval_output=False,branch=None):
        if branch is None:
            con = self.repo.get_contents(file_path,ref=self.branch).decoded_content.decode("utf-8")
        else:
            con = self.repo.get_contents(file_path,ref=branch).decoded_content.decode("utf-8")
        if eval_output is True:
            return eval(con)
        return con







    def sync(self,file_path,prefer="remote",*,dry=False):
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



    def push_file(self,file_path,*,mode = "rb",msg="ShitDB",branch = None):
        with open(file_path,mode) as f:
            content = f.read()
            contents=content
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
