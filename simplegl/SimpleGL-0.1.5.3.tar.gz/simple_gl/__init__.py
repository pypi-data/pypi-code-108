# -*- coding: utf-8 -*- 
# @Time : 9/29/21 9:31 AM 
# @Author : mxt
# @File : __init__.py
from simple_gl.projects import Projects
from simple_gl.groups import Groups
from simple_gl.hooks import Hooks
from simple_gl.branches import Branches
from simple_gl.commits import Commits
from simple_gl.merge_request import MergeRequests


class GLObject:
    def __init__(self, url: str = "", private_token: str = ""):
        self.projects = Projects(url, private_token)
        self.groups = Groups(url, private_token)
        self.hooks = Hooks(url, private_token)
        self.branches = Branches(url, private_token)
        self.commits = Commits(url, private_token)
        self.merge_requests = MergeRequests(url, private_token)
