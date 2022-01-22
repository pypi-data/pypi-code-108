#!/usr/bin/python
#coding:utf-8

#通过jira过滤器，捞出jira类型为critical类型且未添加备注信息的jira
#邮件通知给对应工程师，并抄送经理

import os
import sys
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1,BASE_PATH)

import re
import xlrd
import json
import time
import datetime
from pathlib import Path

import poplib
import smtplib
import telnetlib
import email
import email.policy
from email.parser import Parser
from email.header import Header
from email.header import decode_header
from email.utils import parseaddr
from email.mime.text import MIMEText

from pyocs import pyocs_jira
from pyocs import pyocs_confluence
from pyocs.pyocs_filesystem import PyocsFileSystem
from pyocs.pyocs_login import PyocsLogin

from logUtils.logUtils import logUtils

loggger = logUtils("CriticalJira").log


CUR_PATH = os.path.dirname(os.path.abspath(__file__))
JiraSpecialMemberNameFile = CUR_PATH + "/jira_special_member_name.json"

#发件人
sender_mail = PyocsLogin().get_account_from_json_file()['Username'] + "@cvte.com"
password    = PyocsLogin().get_account_from_json_file()['Password']

#下面这些人的jira账号比较特殊
#需要做一下映射
with open(JiraSpecialMemberNameFile, 'r', encoding='UTF-8') as f:
    special_member = json.loads(f.read())

faenamexls_name="超7天未更新和超期jira提醒.xls"
home_dir = os.environ['HOME']
workspace = home_dir + '/'
workfilepath=workspace+faenamexls_name
order_list = list()
ocsstr=""


#处理JIRA预警信息
def deal_jira_warning_tips(assignee,deadline_time,title,issue_key):
    msg = "\n\n【FAE】: "+assignee+"\n【到期日】: "+deadline_time+"\n【JIRA链接】: https://jira.cvte.com/browse/"+issue_key+"\n【JIRA标题】: "+title
    return msg

def send_email(receivers_mail,cc_mail,mail_text,mail_subject):
    message = MIMEText(mail_text, 'plain')
    #发件人
    message['From'] = Header(sender_mail)
    #收件人
    message['To'] =  Header(receivers_mail)
    #抄送人
    message['Cc'] =  Header(cc_mail)
    #主题
    Subject = mail_subject
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender_mail, password) #邮箱账号
        smtpObj.sendmail(sender_mail, receivers_mail.split(',')+cc_mail.split(','), message.as_string())
        smtpObj.quit();
        loggger.info(receivers_mail + " 邮件发送成功")
    except smtplib.SMTPException:
        loggger.debug(receivers_mail + " 无法发送邮件")


def download_file_form_drive():
    #从坚果云下载FAE姓名表格
    if Path(workfilepath).exists() is True:
        os.remove(workfilepath)
    kb = pyocs_confluence.PyocsConfluence()
    map_list = kb.get_osm_distribute_mapping_info_by_user(faenamexls_name)
    download_link = map_list[0]
    PyocsFileSystem.get_file_from_nut_driver(download_link, workspace)

#获取fae对应的技术经理及fae中文名
def get_fae_info():
    work_book = xlrd.open_workbook(workfilepath)
    work_sheet = work_book.sheet_by_name('NameTab')

    ret = {}
    # 'chinese_name'所在列为1，'pinyin_name'所在列为2，'manager_name'所在列为3；
    # 为了缩小代码量，此处直接使用硬编码
    for row in range(1, work_sheet.nrows):
        chinese_name = str(work_sheet.cell_value(row, 1))
        pinyin_name = str(work_sheet.cell_value(row, 2))
        manager_name = str(work_sheet.cell_value(row, 3))
        ret[pinyin_name] = [chinese_name,manager_name]

    return ret


if __name__ == "__main__":
    #先从坚果云上下载资料待用
    download_file_form_drive()
    fae_info = get_fae_info()

    j = pyocs_jira.JiraCVTE()
    search_content = "status = 新建 AND cf[18011]  is EMPTY  AND 缺陷级别 = Critical AND assignee in (membersOf(dep.tv_tsc_sw_pt1), membersOf(dep.tv_tsc_sw_hd1), membersOf(dep.tv_tsc_sw_hd2), membersOf(dep.tv_tsc_sw_pp1), membersOf(dep.tv_tsc_sw_hn2), membersOf(dep.tv_tsc_sw_hn1), membersOf(dep.tv_tsc_sw_lm))  AND issuetype in (subTaskIssueTypes(), 任务, 子缺陷)"
    # search_content = "status = 新建 AND cf[18011]  is EMPTY  AND 缺陷级别 = Critical AND assignee in membersOf(dep.tv_tsc_sw_lm) AND issuetype in (subTaskIssueTypes(), 任务, 子缺陷)"
    jira_list = j.get_issue_jira_key_list(search_content)

    mail_text = {}
    for issue_key in jira_list:
        issue_info = j.get_issue_jira_import_info(issue_key)
        title = "" if issue_info["title"] is None else issue_info["title"]
        assignee = "" if issue_info["assignee"] is None else issue_info["assignee"]
        deadline_time = "" if issue_info["deadline_time"] is None else issue_info["deadline_time"]

        if assignee in special_member.keys():
            assignee = special_member[assignee]
        try:
            fae_chinese_name = fae_info[assignee][0]
        except:
            loggger.debug("找不到此jira的fae：" + issue_key + ";fae 对应的assignee为：" + assignee)
            continue

        if assignee in mail_text.keys():
            mail_text[assignee] = mail_text[assignee] + deal_jira_warning_tips(fae_chinese_name,deadline_time,title,issue_key)
        else:
            mail_text[assignee] = deal_jira_warning_tips(fae_chinese_name,deadline_time,title,issue_key)
    mail_subject = '《Critical类JIRA待评估备注》'+time.strftime("%Y%m%d", time.localtime())

    mail_text_first_line = "\n以下critical 问题如无法立即处理，请评估后添加备注信息，谢谢！\n\n\n特别注意：按照最新的jira操作规范要求，TVS空间的Critical问题按照每周统计扣除绩效"
    mail_text_last_line = "\n\n\n此信息由脚本自动发送，请勿回复，谢谢！"
    for key in mail_text:
        try:
            #获取fae的技术经理
            cc_mail = fae_info[key][-1] + "@cvte.com"
            if cc_mail == "liyangqiu@cvte.com":
                cc_mail = cc_mail + ",chenchaoxiong@cvte.com"
        except:
            loggger.debug("找不到对应的技术经理：" + key)
            continue
        receivers_mail = key + "@cvte.com"
        # print(receivers_mail)
        # print(cc_mail)
        # print(mail_text_first_line + mail_text[key] + mail_text_last_line,mail_subject)
        send_email(receivers_mail,cc_mail,mail_text_first_line + mail_text[key] + mail_text_last_line,mail_subject)
