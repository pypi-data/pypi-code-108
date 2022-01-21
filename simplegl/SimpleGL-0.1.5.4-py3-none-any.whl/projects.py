# -*- coding: utf-8 -*- 
# @Time : 10/8/21 2:51 PM 
# @Author : mxt
# @File : projects.py
import yaml
import logging
from typing import *
from simple_gl.gitlab_base import GitLabBase


class Projects(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Projects, self).__init__(url=url, private_token=private_token)
        self._project_config_id = 1706

    # 获取工程信息
    def get_project_info(self, project_id: Union[str, int], statistics: bool = False,
                         _license: bool = False, with_custom_attributes: bool = False):
        try:
            project = self.gl.projects.get(
                id=project_id,
                statistics=statistics,
                license=_license,
                with_custom_attributes=with_custom_attributes
            )
            return project.attributes
        except Exception as e:
            logging.getLogger(__name__).error("Projects.get_project_info.error: %s" % str(e))
            return False

    def get_config(self, system_simple_name: str = "", file_type: str = "json", ref: str = "master") -> None:
        try:
            project = self.gl.projects.get(self._project_config_id)
            file = project.files.get(file_path=f"{system_simple_name.upper()}/config.{file_type}", ref=ref)
            file_content = file.decode().decode('utf-8')
            with open(f"{system_simple_name.upper()}/config.{file_type}", "w+", encoding="utf-8") as f:
                f.write(file_content)
            with open(f"{system_simple_name.upper()}/config.{file_type}", "r", encoding="utf-8") as f:
                config = yaml.load(f)
            return config
        except Exception as e:
            logging.getLogger(__name__).error("Projects.get_config.error: %s" % str(e))
            return None
