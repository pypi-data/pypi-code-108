# -*- coding: utf-8 -*- 
# @Time : 10/26/21 2:45 PM 
# @Author : mxt
# @File : merge_request.py
import logging
from typing import *
from .utils import time_format, get_time_diff
from simple_gl.gitlab_base import GitLabBase, MergeRequestResponse


class MergeRequests(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(MergeRequests, self).__init__(url=url, private_token=private_token)

    # 关闭合并请求
    def close_merge_request(self, project_id: Union[str, int], mr_id: int = 1):
        try:
            project = self.gl.projects.get(project_id)
            project.mergerequests.delete(mr_id)
        except Exception as e:
            logging.getLogger(__name__).error("MergeRequests.close_merge_request.error: %s" % str(e))
            return False

    # 代码合并
    def merge_requests(self, project_id: Union[str, int], source_branch: str = "", target_branch: str = "",
                       title: str = "", description: str = ""):
        try:
            project = self.gl.projects.get(project_id)
            try:
                mr = project.mergerequests.create({
                    "source_branch": source_branch,
                    "target_branch": target_branch,
                    "title": title,
                    "description": description
                })
            except Exception as e:
                mr = project.mergerequests.list(
                    source_branch=source_branch,
                    target_branch=target_branch,
                    state="opened"
                )[0]
            attr = mr.changes()
            name = attr.get("author").get("name")
            username = attr.get("author").get("username")
            if attr.get("diff_refs") is None:
                status = "0"
                navigate_to = ""
                message = u"由%s(%s)发起的合并请求：%s合并至%s，合并成功，正在触发流水线。" % (
                    name, username, source_branch, target_branch
                )
            else:
                base_sha = attr.get("diff_refs").get("base_sha")
                head_sha = attr.get("diff_refs").get("head_sha")
                created_at = get_time_diff(time_format(attr.get("created_at")))
                if attr.get("merge_status") == "can_be_merged":
                    mr.merge()
                    status = "0"
                    navigate_to = ""
                    message = u"由%s(%s)发起的合并请求：%s合并至%s，合并成功，正在触发流水线。" % (
                        name, username, source_branch, target_branch
                    )
                else:
                    status = "2" if base_sha == head_sha else "3"
                    navigate_to = "/".join(attr.get("web_url").split("/")[3:])
                    message = u"%s由%s(%s)发起的合并请求：%s合并至%s请求失败，请处理后再次发起。" % (
                        created_at, name, username, source_branch, target_branch
                    )
            return MergeRequestResponse(
                status=status, message=message, navigateTo=navigate_to
            )
        except Exception as e:
            logging.getLogger(__name__).error("MergeRequests.merge_requests.error: %s" % str(e))
            return False
