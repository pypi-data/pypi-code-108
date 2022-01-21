# -*- coding: utf-8 -*- 
# @Time : 10/8/21 2:59 PM 
# @Author : mxt
# @File : groups.py
import logging
from simple_gl.gitlab_base import GitLabBase


class Groups(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Groups, self).__init__(url=url, private_token=private_token)

    # 创建组
    def create_groups(self, name: str = "", path: str = "", description: str = "", visibility: str = "private",
                      lfs_enabled: bool = False, request_access_enabled: bool = False):
        try:
            group = self.gl.groups.create({
                "name": name.upper(), "path": path, "description": description, "visibility": visibility,
                "lfs_enabled": lfs_enabled, "request_access_enabled": request_access_enabled
            })
            return group
        except Exception as e:
            logging.getLogger(__name__).error("Groups.create_groups.error: %s" % str(e))
            return False
