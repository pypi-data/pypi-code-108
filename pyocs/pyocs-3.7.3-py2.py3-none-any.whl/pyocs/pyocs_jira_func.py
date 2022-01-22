import time
import datetime
from pyocs import pyocs_jira

class PyocsJiraFunc:
    jiar_obj = None

    def __init__(self):
        self.jiar_obj = pyocs_jira.JiraCVTE()
    
    def get_tv_tsc_team_search_closed_content(self, team_name):
        search_issues_closed_head = 'issuetype in (缺陷, 子缺陷, 软件缺陷, 软件功能, DQC缺陷, DQC子缺陷) \
        AND assignee in (membersOf('

        search_issues_closed_tail = ')) \
        AND (filter = 20133 OR project in (FAC, DQC, TVS)) \
        AND filter not in (26584, 26583) AND filter = 42388 \
        AND (项目状态 = EMPTY OR 项目状态 = 项目正常) \
        AND (created <= startOfMonth(25d) \
        AND status in (新建, 重新打开, "In Progress", 处理中, 重新打开, 打回, 已分派) \
        AND (due <= -1d OR due is EMPTY AND created <= startOfDay(-8d)) OR status in (已审核, 关闭, 测试中) \
        AND (关闭日期 >= startOfMonth(-4d) \
        AND 关闭日期 < startOfMonth(25d) OR resolutiondate >= startOfMonth(-4d) \
        AND resolutiondate <= startOfMonth(25d))) \
        AND created >= 2017-06-01 ORDER BY assignee DESC, cf[11110] ASC, created ASC, status DESC'

        search_task_closed_head = 'issuetype in (任务, 子任务, 子需求, 技术任务) \
        AND assignee in (membersOf('

        search_task_closed_tail = ')) \
        AND (filter = 20133 OR project in (FAC, DQC, TVS)) \
        AND filter not in (26584, 26583) AND filter = 42388 \
        AND (项目状态 = EMPTY OR 项目状态 = 项目正常) \
        AND (created <= startOfMonth(25d) \
        AND status in (新建, 重新打开, "In Progress", 处理中, 重新打开, 打回, 已分派) \
        AND due <= -1d OR status in (已审核, 关闭) \
        AND due <= -1d AND (关闭日期 >= startOfMonth(-4d) AND 关闭日期 < startOfMonth(25d) OR resolutiondate >= startOfMonth(-4d) \
        AND resolutiondate <= startOfMonth(25d))) AND created >= 2017-06-01 ORDER BY status DESC, due DESC'

        search_team = ''

        if team_name == "BT1":
            search_team = 'dep.tv_tsc_sw_hd1'
        elif team_name == "BT3":
            search_team = 'dep.tv_tsc_sw_lm'
        elif team_name == "BT5":
            search_team = 'dep.tv_tsc_sw_hn1'
        elif team_name == "BT6":
            search_team = 'dep.tv_tsc_sw_hn2'
        elif team_name == "BT7":
            search_team = 'dep.tv_tsc_sw_pp1'
        elif team_name == "PT1":
            search_team = 'dep.tv_tsc_sw_pt1'

        issues_search_closed_content = search_issues_closed_head + search_team + search_issues_closed_tail
        task_search_closed_content = search_task_closed_head + search_team + search_task_closed_tail

        return (issues_search_closed_content, task_search_closed_content)

    def get_tv_tsc_team_search_unclosed_content(self, team_name):
        search_issues_unclosed_head = 'issuetype in (缺陷, 子缺陷, 软件缺陷, 软件功能) AND assignee in (membersOf('

        search_issues_unclosed_tail = ')) AND (RD协作处理人 in (无) OR RD协作处理人 is EMPTY OR RD协作处理人 in (membersOf(dep.tsc)))\
             AND status in (新建, 重新打开, "In Progress", 待挂起, 处理中)'

        search_task_unclosed_head = 'project = TVS AND status in (新建, 处理中, 重新打开) AND assignee in (membersOf('

        search_task_unclosed_tail = ')) ORDER BY created ASC, issuetype DESC, status ASC, priority DESC, updated DESC'

        search_team = ''

        if team_name == "BT1":
            search_team = 'dep.tv_tsc_sw_hd1'
        elif team_name == "BT3":
            search_team = 'dep.tv_tsc_sw_lm'
        elif team_name == "BT5":
            search_team = 'dep.tv_tsc_sw_hn1'
        elif team_name == "BT6":
            search_team = 'dep.tv_tsc_sw_hn2'
        elif team_name == "BT7":
            search_team = 'dep.tv_tsc_sw_pp1'
        elif team_name == "PT1":
            search_team = 'dep.tv_tsc_sw_pt1'

        issues_search_unclosed_content = search_issues_unclosed_head + search_team + search_issues_unclosed_tail
        task_search_unclosed_content = search_task_unclosed_head + search_team + search_task_unclosed_tail

        return (issues_search_unclosed_content, task_search_unclosed_content)

    def valid_time(self, timestr):
        valid_time = None
        try:
            valid_time = time.mktime(time.strptime(timestr, '%Y-%m-%d'))
        except Exception  as identifier:
            print(identifier)
        
        if (valid_time != None):
            valid_time = int(valid_time)

        return valid_time


    def get_overdue_closed_issue(self, search_content):
        deadline_time = None
        resolve_time = None
        finish_time = None
        close_time = None
        submit_test_time = None

        issues_key_list = self.jiar_obj.get_issue_jira_key_list(search_content)
        
        issues_overdue_list = list()

        for issue_key in issues_key_list:
            issue_info = self.jiar_obj.get_issue_jira_import_info(issue_key)
            title = issue_info["title"]
            assignee = issue_info["assignee"]
            deadline_time = issue_info["deadline_time"]
            resolve_time = issue_info["resolve_time"]
            finish_time = issue_info["finish_time"]
            close_time = issue_info["close_time"]
            submit_test_time = issue_info["submit_test_time"]

            if (deadline_time != None):
                 deadline_time = self.valid_time(deadline_time)
            if (resolve_time != None):
                 resolve_time = self.valid_time(resolve_time)
            if (finish_time != None):
                 finish_time = self.valid_time(finish_time)
            if (close_time != None):
                 close_time = self.valid_time(close_time)
            if (submit_test_time != None):
                 submit_test_time = self.valid_time(submit_test_time)

            #提交测试时间 关闭时间 完成时间 解决时间 其中之一小于等于到期时间均为正常，否则视为超期
            time_list = list()
            time_list.append(resolve_time)
            time_list.append(finish_time)
            time_list.append(close_time)
            time_list.append(submit_test_time)

            over_due_flag = True
            for i in range(0, len(time_list)):
                if (time_list[i] != None and deadline_time != None):
                    if (time_list[i] - deadline_time <= 0):
                        over_due_flag = False
                        break

            if over_due_flag :
                print(issue_key + "  " + assignee + "  "+ title)
                issues_overdue_list.append(issue_key)

        return (issues_overdue_list, issues_key_list)


    def get_overdue_unclosed_issue(self, search_content):
        deadline_time = None
        issues_key_list = self.jiar_obj.get_issue_jira_key_list(search_content)
        
        issues_overdue_list = list()
        current_time_origin = datetime.datetime.now()
        current_time_str = current_time_origin.strftime("%Y-%m-%d")
        current_time = self.valid_time(current_time_str)

        for issue_key in issues_key_list:
            issue_info = self.jiar_obj.get_issue_jira_import_info(issue_key)
            title = issue_info["title"]
            assignee = issue_info["assignee"]
            deadline_time = issue_info["deadline_time"]

            if (deadline_time != None):
                 deadline_time = self.valid_time(deadline_time)

            #未关闭的问题当前时间大于到期时间为超期
            if (current_time > deadline_time):
                print(issue_key + "  " + assignee + "  "+ title)
                issues_overdue_list.append(issue_key)

        return (issues_overdue_list, issues_key_list)


    def calculate_the_overdue_rate(self, team_name):
        search_closed_content = self.get_tv_tsc_team_search_closed_content(team_name)
        search_unclosed_content = self.get_tv_tsc_team_search_unclosed_content(team_name)
        print ("------------------------------------------超期缺陷如下---------------------------------------------")
        issue_closed_tuple = self.get_overdue_closed_issue(search_closed_content[0])
        issue_unclosed_tuple = self.get_overdue_unclosed_issue(search_unclosed_content[0])
        print ("------------------------------------------超期任务如下---------------------------------------------")
        task_closed_tuple = self.get_overdue_closed_issue(search_closed_content[1])
        task_unclosed_tuple = self.get_overdue_unclosed_issue(search_unclosed_content[1])
        
        overdue_issue = len(issue_closed_tuple[0]) + len(issue_unclosed_tuple[0])
        all_issue = len(issue_closed_tuple[1]) + len(issue_unclosed_tuple[1])
        overdue_issue_rate = int((overdue_issue/all_issue)*100)

        print ("------------------------------------------超期比率如下---------------------------------------------")
        print ("超期缺陷数量:" + str(overdue_issue))
        print ("总的缺陷数量:" + str(all_issue))
        print ("超期缺陷比率:" + str(overdue_issue_rate) + "%")


        overdue_task = len(task_closed_tuple[0]) + len(task_unclosed_tuple[0])
        all_task = len(task_closed_tuple[1]) + len(task_unclosed_tuple[1])
        overdue_task_rate = int((overdue_task/all_task)*100)
        
        print ("超期任务数量:" + str(overdue_task))
        print ("总的任务数量:" + str(all_task))
        print ("超期任务比率:" + str(overdue_task_rate) + "%")


if __name__ == "__main__":
    pjf = PyocsJiraFunc()
    pjf.calculate_the_overdue_rate('BT5')
