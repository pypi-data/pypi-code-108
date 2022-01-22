#coding:utf-8
from jira import JIRA
import arrow
import xlwt
import json

######################################################Need Config ################################################################
HISENSE_USER_NAME = ''  # 请输入海信jira的用户名
HISENSE_PWD = ''      # 请输入海信jira的密码
CVTE_USER_NAME = ''        # 请输入CVTE jira的用户名
CVTE_PWD = ''              # 请输入CVTE jira的密码

HISENSE_JIRA_URL = ""
CVTE_JIRA_URL = ""
HISENSE_JIRA_FILTER = ''
CVTE_SPACE = ''
CVTE_PROJECT = []
CVTE_ASSIGN_L1 = []
CVTE_ASSIGN_L2 = []
CVTE_PROORITY = []


DEFAULT_ASSIGN = ""
DEFAULT_PROJECT = ""
DEFAULT_PRORITY = ""
DEFAULT_LAB = ""
GROUND = ""

XLSFILE = 'differenec.xls'


def CreateIssue(jira,project,program,summary,description, assignee,priority,lab):
    issue_dict = {
        'project': {'key': project},
        'issuetype': {'name': '任务'},
        'summary': '%s' % (summary),
        'description': description,
        'assignee': {'name': assignee},
        'customfield_12803': {'value': program}, #方案
        'customfield_12804': {'value': GROUND},  # 所属战队
        'labels':lab,
        'priority':{'name': priority},
        "duedate":"%s"%DUEDAY
    }
    jira.create_issue(issue_dict)

def SwtichCvteStatus2Hisense(cvtestatus):
    result = cvtestatus
    if(cvtestatus.encode('gbk') == str('新建').encode('gbk') or cvtestatus.encode('gbk') == str('进行中').encode('gbk')):
        result = str('Open')
    return result


if __name__ == '__main__':
    print("Begin ......")
    print("正在读取json文件...")
#读取json文件
    with open("cvte_data.json", 'r', encoding='UTF-8') as f:
        temp = json.loads(f.read())

        HISENSE_JIRA_URL = temp["hx_jira"]["url"]
        CVTE_JIRA_URL = temp["cvt_jira"]["url"]

        HISENSE_USER_NAME = temp["hx_jira"]["user"]
        HISENSE_PWD = temp["hx_jira"]["password"]
        CVTE_USER_NAME = temp["cvt_jira"]["user"]
        CVTE_PWD = temp["cvt_jira"]["password"]

        HISENSE_JIRA_FILTER = temp["hx_jira"]["filter"]
        CVTE_SPACE = temp["cvt_jira"]["space"]

        DEFAULT_ASSIGN = temp["dafault_data"]["assign"]
        DEFAULT_PROJECT = temp["dafault_data"]["project"]
        DEFAULT_PRORITY = temp["dafault_data"]["prority"]
        DEFAULT_LAB = temp["dafault_data"]["lab"]
        GROUND = temp["dafault_data"]["ground"]

        CVTE_PROJECT = temp["switch_data"]["project"]
        CVTE_ASSIGN_L1 = temp["switch_data"]["assign_l1"]
        CVTE_ASSIGN_L2 = temp["switch_data"]["assign_l2"]
        CVTE_PROORITY = temp["switch_data"]["prority"]

#获取时间，补充jira过滤器
    today = arrow.now()
    DATE = int(today.format("DD"))

    if DATE <= 10:
        DUEDAY = today.shift(months=+1).format("YYYY-MM-01")
        end_time = today.shift(months=+1).format("YYYY-MM-01")
        start_time = today.shift(months=-1).format("YYYY-MM-01")
    else:
        DUEDAY = today.shift(months=+2).format("YYYY-MM-01")
        end_time = today.shift(months=+1).format("YYYY-MM-01")
        start_time = today.shift(months=-1).format("YYYY-MM-01")

    jira_data = " AND created >= " + start_time + " AND " + "created < " + end_time
    HISENSE_JIRA_FILTER = HISENSE_JIRA_FILTER + " " + jira_data

    print("正在登陆jira...")

    HisenseJira = JIRA(HISENSE_JIRA_URL,basic_auth=(HISENSE_USER_NAME,HISENSE_PWD))
    CvteJira = JIRA(CVTE_JIRA_URL, basic_auth=(CVTE_USER_NAME,CVTE_PWD))

#初始化excel表格
    excel = xlwt.Workbook()
    sheet = excel.add_sheet('sheet1')
    column = 0
    row = 0
    n = 0
    rowlist = ['Hisense ID', 'CVTE ID', '主题', 'CVTE Status', 'Hisense Status']
    for column in range(0, len(rowlist)):
        sheet.write(row, column, rowlist[column])
    row += 1

#遍历海信JIRA问题
    print("开始遍历jira问题...")
    for issue in HisenseJira.search_issues(HISENSE_JIRA_FILTER,startAt=0,maxResults=5000):
        print("\n---------------------------------------------------\n")
        LoopIssue = HisenseJira.issue(issue)
        print(LoopIssue.key,LoopIssue.fields.summary)

        #查找CVTE jira相同摘要问题
        GetCVTEIssue = CvteJira.search_issues('project = %s AND issuetype = 任务 AND text ~ "【%s】"'%(CVTE_SPACE,LoopIssue.key),startAt=0,maxResults=5000)

        if(any(GetCVTEIssue)):
            print("查找到相同的jira")
            CvteIssue = CvteJira.issue(GetCVTEIssue[0])
            if (str(LoopIssue.fields.status).encode('gbk') != SwtichCvteStatus2Hisense(str(CvteIssue.fields.status)).encode('gbk')):
                IssueList = [LoopIssue.key, CvteIssue.key, CvteIssue.fields.summary, CvteIssue.fields.status,LoopIssue.fields.status]

                for column in range(0, len(rowlist)):
                    sheet.write(row, column, str(IssueList[column]))
                row += 1
                column = 0
        else:
            print("新建jira")
            ASSIGN = DEFAULT_ASSIGN
            PROJECT = DEFAULT_PROJECT
            PRORITY = DEFAULT_PRORITY

            #获取项目映射
            for member in CVTE_PROJECT:
                if member.split(' ')[0] in str(LoopIssue.key).split('-')[0]:
                    PROJECT = member.split(' ')[1]
                    break

            #获取经办人映射
            for member in CVTE_ASSIGN_L1:
                if member.split(' ')[0] in str(LoopIssue.fields.assignee):
                    ASSIGN = member.split(' ')[1]
                    break

            if ASSIGN == DEFAULT_ASSIGN:
                 for member in CVTE_ASSIGN_L2:
                     if member.split(' ')[0] in str(LoopIssue.key).split('-')[0]:
                         ASSIGN = member.split(' ')[1]
                         break

            #获取优先级映射
            for member in CVTE_PROORITY:
                if member.split(' ')[0] in str(LoopIssue.fields.priority):
                    PRORITY = member.split(' ')[1]
                    break

            #添加标签
            lab1 = lab2 = lab3 = "None"
            if LoopIssue.fields.customfield_10005:
                lab1 = (str(LoopIssue.fields.customfield_10005))
            if LoopIssue.fields.customfield_10900:
                lab2 = (str(LoopIssue.fields.customfield_10900))
            if len(LoopIssue.fields.versions) != 0:
                lab3 = (str(LoopIssue.fields.versions[0]))

            lab = [lab1,lab3,lab2,DEFAULT_LAB]

            SUMMARY = "【" + str(LoopIssue.key) + "】"+str(LoopIssue.fields.summary)

            CreateIssue(CvteJira,CVTE_SPACE,PROJECT,SUMMARY,str(LoopIssue.fields.description),ASSIGN,PRORITY,lab)

    excel.save(XLSFILE)

