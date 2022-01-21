# -*- coding: utf-8 -*- 
# @Time : 10/8/21 2:59 PM 
# @Author : mxt
# @File : branches.py
import logging
from typing import *
from simple_gl.gitlab_base import GitLabBase, MergeRequestResponse


class Branches(GitLabBase):
    def __init__(self, url: str = "", private_token: str = ""):
        super(Branches, self).__init__(url=url, private_token=private_token)

    # 创建分支
    def create_branch(self, project_id: Union[str, int], branch: str = "", ref: str = "master"):
        try:
            project = self.gl.projects.get(project_id)
            _branch = project.branches.create({
                "branch": branch,
                "ref": ref
            })
            return _branch
        except Exception as e:
            logging.getLogger(__name__).error("Branches.create_branch.error: %s" % str(e))
            return False

    # 删除分支
    def delete_branch(self, project_id: Union[str, int], branch: str = ""):
        try:
            project = self.gl.projects.get(project_id)
            project.branches.delete(branch)
        except Exception as e:
            logging.getLogger(__name__).error("Branches.delete_branch.error: %s" % str(e))

    # 保护分支
    def protect_branch(self, project_id: Union[str, int], branch: str = "",
                       developers_can_push: bool = True, developers_can_merge: bool = True):
        try:
            project = self.gl.projects.get(project_id)
            _branch = project.branches.get(branch)
            _branch.protect(developers_can_push=developers_can_push, developers_can_merge=developers_can_merge)
        except Exception as e:
            logging.getLogger(__name__).error("Branches.protect_branch.error: %s" % str(e))

    # 查询分支
    def search_branch(self, project_id: Union[str, int], branch: str = "dev"):
        status = 0
        try:
            project = self.gl.projects.get(project_id)
            branches = [_ for _ in project.branches.list(search=branch) if _.attributes["name"] == branch]
            if len(branches) == 1:
                status = 1
        except Exception as e:
            status = 0
            logging.getLogger(__name__).error("Branches.protect_branch.error: %s" % str(e))
        return status

    # 判断分支是否存在
    def temporary_branch_create(self, project_id: Union[str, int], branch: str = "dev"):
        try:
            project = self.gl.projects.get(project_id)
            branches = [_ for _ in project.branches.list(search=branch) if _.attributes["name"] == branch]
            if len(branches) == 1:
                branches[0].delete()
                self.create_branch(project_id, branch)
                status = 0
                navigate_to = ""
                message = u"应用%s存在%s分支，已删除原有%s分支并重新创建，可继续合并代码" % (
                    project.attributes["name"], branch, branch)
            else:
                create_branch_status = self.create_branch(project_id, branch)
                if isinstance(create_branch_status, bool):
                    error_branches = [_.attributes["name"] for _ in project.branches.list(search=branch)]
                    status = 1
                    navigate_to = project.attributes["web_url"] + "/branches/all"
                    message = u"应用%s下存在不合规分支：%s，请删除不合规分支后重新发起" % (
                        project.attributes["name"], "、".join(error_branches)
                    )
                else:
                    status = 0
                    navigate_to = ""
                    message = u"自动为应用%s创建%s分支，可继续合并代码" % (project.attributes["name"], branch)
            return MergeRequestResponse(status=status, navigateTo=navigate_to, message=message)
        except Exception as e:
            logging.getLogger(__name__).error("Branches.temporary_branch_create.error: %s" % str(e))

    # 版本分支处理
    def version_branch_create(self, project_id: Union[str, int], branch: str = "dev"):
        try:
            project = self.gl.projects.get(project_id)
            branches = [_ for _ in project.branches.list(search=branch) if _.attributes["name"] == branch]
            if len(branches) == 1:
                status = 0
                navigate_to = ""
                message = u"应用%s存在%s分支，可继续合并代码" % (project.attributes["name"], branch)
            else:
                create_branch_status = self.create_branch(project_id, branch)
                if isinstance(create_branch_status, bool):
                    error_branches = [_.attributes["name"] for _ in project.branches.list(search=branch)]
                    status = 1
                    navigate_to = project.attributes["web_url"] + "/branches/all"
                    message = u"应用%s下存在不合规分支：%s，请删除不合规分支后重新发起" % (
                        project.attributes["name"], "、".join(error_branches)
                    )
                else:
                    status = 0
                    navigate_to = ""
                    message = u"自动为应用%s创建%s分支，可继续合并代码" % (project.attributes["name"], branch)
            return MergeRequestResponse(status=status, navigateTo=navigate_to, message=message)
        except Exception as e:
            logging.getLogger(__name__).error("Branches.version_branch_create.error: %s" % str(e))
