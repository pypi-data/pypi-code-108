# -*- coding: utf-8 -*- 
# @Time : 10/8/21 3:00 PM 
# @Author : mxt
# @File : hooks.py
import logging
from typing import *
from simple_gl.gitlab_base import GitLabBase


class Hooks(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Hooks, self).__init__(url=url, private_token=private_token)

# 创建钩子
    def create_hook(self, project_id: Union[str, int], url: str = "", push_events: bool = True,
                    push_events_branch_filter: str = ""):
        try:
            project = self.gl.projects.get(project_id)
            hooks = [_.attributes.get("id") for _ in project.hooks.list(all=True)
                     if push_events_branch_filter in _.attributes.get("url")]
            if len(hooks) == 0:
                hook = project.hooks.create({
                    "url": url,
                    "push_events": push_events,
                    "push_events_branch_filter": push_events_branch_filter
                })
            else:
                hook = hooks[0]
            return hook
        except Exception as e:
            logging.getLogger(__name__).error("Hooks.create_hook.error: %s" % str(e))
            return False

    # 删除钩子
    def delete_hook(self, project_id: Union[str, int], branch_name: str = ""):
        try:
            project = self.gl.projects.get(project_id)
            hooks = [_.attributes.get("id") for _ in project.hooks.list(all=True)
                     if branch_name in _.attributes.get("url")]
            for hook_id in hooks:
                project.hooks.delete(hook_id)
        except Exception as e:
            logging.getLogger(__name__).error("Hooks.create_hook.error: %s" % str(e))
