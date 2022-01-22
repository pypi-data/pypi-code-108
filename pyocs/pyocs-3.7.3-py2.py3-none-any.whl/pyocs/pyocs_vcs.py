from git import Repo
import os


class PyocsVcs:

    def __init__(self, working_tree_dir):
        self.working_tree_dir = working_tree_dir
        self.repo = Repo(self.working_tree_dir)
        assert not self.repo.bare

    def get_repo_project(self):
        """获取此git仓库对应的方案名
        Args:
        Returns:
             返回对应tv方案名
        """
        remote_url = self.repo.remotes.origin.url
        tv_project = remote_url.split('/')[-4]
        return tv_project

    def add_commit_gerrit_push(self, file: str, branch: str, commit_message: str):
        self.repo.git.add(file)
        self.repo.git.commit(m=commit_message)
        self.repo.git.pull("origin", "--rebase", branch)
        # self.repo.git.push("origin", "HEAD:refs/for/" + branch + '%submit') 配置管理要求使用 gt-dpush，弃用此方式
        os.chdir(str(self.working_tree_dir))
        with os.popen('git gt-dpush origin ' + branch) as p:
            ret = p.read()
        # 检查是否与远程同步
        self.repo.git.pull("origin", "--rebase", branch)
        if not self.is_local_and_remote_the_same_commit():
            with os.popen('git gt-dpush origin ' + branch) as p:
                ret = p.read()
        return ret

    def is_local_and_remote_the_same_commit(self):
        local_commit = self.repo.commit()
        remote_commit = self.repo.remotes.origin.fetch()[0].commit
        return local_commit.hexsha == remote_commit.hexsha

    def add_commit_git_push(self, file: str, branch: str, commit_message: str):
        self.repo.git.add(file)
        self.repo.git.commit(m=commit_message)
        self.repo.git.push("origin", "HEAD:" + branch)

    def git_checkout(self, branch):
        self.repo.remotes.origin.fetch()
        self.repo.git.checkout(branch)

    def git_update(self, branch):
        self.repo.head.reset('HEAD~1', index=True, working_tree=True)
        self.repo.git.pull("origin", branch+":"+branch)
