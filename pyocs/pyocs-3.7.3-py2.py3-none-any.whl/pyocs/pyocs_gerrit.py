import os
import sys
from pathlib import Path
from datetime import datetime
from pyocs.pyocs_confluence import PyocsConfluence

class PyocsGerrit:

    
    def __init__(self):
        self.assignee_confluence_page_id = "184943467"

    def get_current_time_weekday(self):
        """获取当前星期数
        Returns:
            返回当天为星期数字
        """
        time_weekday = datetime.today().isoweekday()
        return time_weekday

    def execCmd(self,cmd):
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text

    def get_code_info(self):
        """获取当前代码仓库
        Returns:
            返回当前路径的代码仓库名
        """
        remote_list = self.execCmd('git remote -v')
        git_path = Path('.git')
        if not git_path.exists():
            print("请在git仓库路径下执行此命令")
            return None
        project_name = str(remote_list).split('\n')[0].split('/')[3]
        return project_name

    def get_assignee_from_conflunce(self):
        """获取当前代码的审核人
        Returns:
            返回当前代码当天代码审核人邮件地址
        """
        code_info = self.get_code_info()
        if code_info is None:
            return None
        assignee_group = PyocsConfluence().get_kb_tables_page_content(self.assignee_confluence_page_id,str(code_info))
        if assignee_group is None:
            return None
        curr_time = self.get_current_time_weekday()
        assignee_info_list = assignee_group[str(curr_time)]
        assignee_person_emailaddr = assignee_info_list[-1] #取后面的邮件地址
        return assignee_person_emailaddr

    def gerrit_gtpush(self):
        getGitSHA = self.execCmd('git rev-parse --short HEAD')
        getGitBranch = self.execCmd('git symbolic-ref --short -q HEAD')
        BranchStr = str(getGitBranch).replace('\n','')
        Reviewer = self.get_assignee_from_conflunce(BranchStr)
        ReviewerStr = str(Reviewer).replace('\n','')
        os.system('git reset HEAD^^ --hard')
        os.system('git pull')
        os.system('git cherry-pick '+getGitSHA)
        gtpushcmd = 'git push origin HEAD:refs/for/'+BranchStr+'%r='+ReviewerStr+',r='+ReviewerStr
        print('cmd = ' + gtpushcmd)
        os.system(gtpushcmd)
