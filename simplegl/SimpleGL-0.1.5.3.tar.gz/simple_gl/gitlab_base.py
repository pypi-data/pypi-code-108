# -*- coding: utf-8 -*- 
# @Time : 10/8/21 2:51 PM 
# @Author : mxt
# @File : gitlab_base.py
import gitlab
from pydantic import BaseModel


class MergeRequestResponse(BaseModel):
    status: int = 0
    message: str = "Error"
    navigateTo: str = ""


def response(status: int = 0, message: str = "Error", navigate_to: str = "/")-> MergeRequestResponse:
    return MergeRequestResponse(status=status, message=message, navigateTo=navigate_to)


class GitLabBase:
    def __init__(self, url: str = "", private_token: str = ""):
        self.gl = gitlab.Gitlab(url=url, private_token=private_token)
