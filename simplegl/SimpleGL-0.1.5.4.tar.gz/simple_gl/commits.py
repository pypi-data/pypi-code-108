# -*- coding: utf-8 -*- 
# @Time : 10/8/21 3:09 PM 
# @Author : mxt
# @File : commits.py
import logging
from typing import *
from simple_gl.gitlab_base import GitLabBase
from code_analysis import CodeAnalysis


class Commits(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Commits, self).__init__(url=url, private_token=private_token)

    # 获取diff信息
    def get_code_diff(self, project_id: Union[str, int], sha: str = "00000000"):
        try:
            project = self.gl.projects.get(id=project_id)
            commit = project.commits.get(sha)
            data = CodeAnalysis(datas=commit.diff())
            return data.result()
        except Exception as e:
            logging.getLogger(__name__).error("Commits.get_code_diff.error: %s" % str(e))
            return False
