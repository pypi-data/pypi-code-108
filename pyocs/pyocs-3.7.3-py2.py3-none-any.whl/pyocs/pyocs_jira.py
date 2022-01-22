from jira import JIRA
from pyocs import pyocs_login


class JiraCVTE(object):
    jira = None

    def __init__(self):
        account = pyocs_login.PyocsLogin().get_account_from_json_file()
        AUTH = (account['Username'], account['Password'])
        OPTIONS = {
            'server': 'https://jira.cvte.com',
        }
        self.jira = JIRA(OPTIONS, basic_auth=AUTH)

    def get_my_jiras(self):
        search_type = "assignee = currentUser() AND resolution = Unresolved ORDER BY updated DESC"
        my_jiras = self.jira.search_issues(search_type)

        return my_jiras

    def print_jiras(self):
        jiras = self.get_my_jiras()
        for j in jiras:
            status = str(j.fields.status)
            if status != '无效':
                print('{}: 【{}】{}'.format(j.key, status, j.fields.summary))

    def print_issue_jira_fields_info(self, issue_key):
        issue = self.jira.issue(issue_key)
        for atrr in dir(issue.fields):
            print(str(atrr) + ": " + str(getattr(issue.fields, atrr)))


    def get_issue_jira_import_info(self, issue_key):
        issue_import_info = {
            "title":None,                   #任务标题
            "assignee":None,                #经办人
            "deadline_time":None,           #到期时间
            "creator":None,                 #创建人
            "create_time":None,             #创建时间
            "resolve_time":None,            #解决时间
            "finish_time":None,             #实际完成时间
            "close_time":None,              #关闭时间
            "submit_test_time":None         #提交测试时间
        }

        issue = self.jira.issue(issue_key)
        issue_import_info["title"] = issue.fields.summary
        issue_import_info["creator"] = issue.fields.creator.key if issue.fields.creator else ''
        issue_import_info["assignee"] = issue.fields.assignee.key if issue.fields.assignee else ''
        if (issue.fields.duedate != None):
            issue_import_info["deadline_time"] = issue.fields.duedate.split('T')[0]
        if (issue.fields.created != None):
            issue_import_info["create_time"] = issue.fields.created.split('T')[0]
        if (issue.fields.resolutiondate != None):
            issue_import_info["resolve_time"] = issue.fields.resolutiondate.split('T')[0]
        if (issue.fields.customfield_11321 != None):
            issue_import_info["finish_time"] = issue.fields.customfield_11321.split('T')[0]
        if (issue.fields.customfield_14204 != None):
            issue_import_info["close_time"] = issue.fields.customfield_14204.split('T')[0]
        if (issue.fields.customfield_16804 != None):
            issue_import_info["submit_test_time"] = issue.fields.customfield_16804.split('T')[0]

        return issue_import_info


    def get_issue_jira_key_list(self, search_content):
        issue_key_list = list()
        issues = self.jira.search_issues(search_content, maxResults=False)
        for issue in issues:
            issue_key_list.append(issue.key)

        return issue_key_list



# j = JiraCVTE()
# jiras = j.get_my_jiras()
# for i in jiras:
#     status = str(i.fields.status)
#     if status != '无效':
#         print('{}: 【{}】{}'.format(i.key, status, i.fields.summary))

if __name__ == "__main__":
    j = JiraCVTE()
    j.print_issue_jira_fields_info("TVS-119896")