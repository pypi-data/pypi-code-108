#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import re
import datetime
import smtplib
from jira import JIRA
import arrow
from email.header import Header
from email.mime.text import MIMEText

jira_server=""
jira_user=""
jira_password=""
mail_sender = ""
mail_password = ""
mail_receivers = ""

open_jira = ""
total_jira = ""
Field_jira = ""
start_time=""
end_time=""

typecount=6

def getJiraData(index):
	AUTH = (jira_user, jira_password)  # JIRA账号
	OPTIONS = {
		'server': jira_server,
	}
	jira = JIRA(OPTIONS, basic_auth=AUTH)
	jira_list = jira.search_issues(index, maxResults=1000)

	return jira_list

def SendEmail():

#本地路径，用于存储调试信息
	if getattr(sys, 'frozen', False):
		pathname = sys._MEIPASS
	else:
		pathname = os.path.split(os.path.realpath(__file__))[0]
	filepath = pathname + "/out.txt"

#获取jira数据
	open_jira_list = getJiraData(open_jira)
	other_jira_list = getJiraData(other_jira)
	total_jira_list = getJiraData(total_jira)


#打开文件，用于保存jira数据到本地
	f = open(filepath, "w")

	open_count = len(open_jira_list)
	other_count = len(other_jira_list)
	total_count = len(total_jira_list)

#other_count 表格数据
	OTHER_JIRA_DATA = list(range(0, typecount * other_count))
	item = 0
	for issues in other_jira_list:
		issue_id=issues.key
		issue_summary=issues.fields.summary
		issue_status=issues.fields.status
		issue_priority=issues.fields.priority
		issue_assignee = issues.fields.assignee
		issue_data = str(issues.fields.created)[0:10]

		OTHER_JIRA_DATA[item * typecount + 0] = str(issue_id)
		OTHER_JIRA_DATA[item * typecount + 1] = str(issue_priority)
		OTHER_JIRA_DATA[item * typecount + 2] = str(issue_status)
		OTHER_JIRA_DATA[item * typecount + 3] = str(issue_data)
		OTHER_JIRA_DATA[item * typecount + 4] = str(issue_assignee)
		OTHER_JIRA_DATA[item * typecount + 5] = str(issue_summary)
		item = item + 1
#end

	JIRA_DATA = list(range(0, typecount * open_count))
	item = 0
	reopen_count = 0
	review_count = 0
	for issues in open_jira_list:
		issue_id=issues.key
		issue_summary=issues.fields.summary
		issue_status=issues.fields.status
		issue_priority=issues.fields.priority
		issue_assignee = issues.fields.assignee
		issue_data = str(issues.fields.created)[0:10]
		if "Reopened" == str(issue_status):
			reopen_count = reopen_count + 1
		if "审批中" == str(issue_status):
			review_count = review_count + 1
		print(issue_data+" "+issue_id+": "+" "+str(issue_priority)+"【"+str(issue_status)+"】"+" "+str(issue_assignee)+" "+str(issue_summary),file=f)

#初始化列表，用于保存数据到html
		JIRA_DATA[item * typecount + 0] = str(issue_id)
		JIRA_DATA[item * typecount + 1] = str(issue_priority)
		JIRA_DATA[item * typecount + 2] = str(issue_status)
		JIRA_DATA[item * typecount + 3] = str(issue_data)
		JIRA_DATA[item * typecount + 4] = str(issue_assignee)
		JIRA_DATA[item * typecount + 5] = str(issue_summary)
		item = item + 1

#计算比例
	close_percentage= str(float('%.2f' % ((total_count-open_count)/total_count*100)))+"%"
	notrepoen_percentage= str(float('%.2f' % ((1-reopen_count/(total_count-open_count))*100)))+"%"

#输出jira数据到out.txt文件
	print("统计时间 ： " + start_time + " - " + end_time,file=f)
	print("total count = " + str(total_count),file=f)
	print("open count = "+str(open_count),file=f)
	print("reopen count = " + str(reopen_count),file=f)
	print('解决率为: '+ close_percentage,file=f)
	print('测试通过率为: '+ notrepoen_percentage,file=f)

	f.close()


#构建邮件内容

	MAIL_TITAL = ('<p style="font-size:120%\"> Dear ALL：\r\n'
				  +'<p style="font-size:120%\">&nbsp&nbsp&nbsp&nbsp如下是本月海信JIRA的90天数据，请关注！</p>\r\n')

	MAIL_TEXT1 = ('<p style="color:blue;font-size:120%\">统计时间  ： '+ str(start_time) + " - " + str(end_time)+'</p>'
				 + '<p style="color:blue;font-size:120%\">总    数： ' + str(total_count) + '</p>'
				 + '<p style="color:blue;font-size:120%\">open  数：' + str(open_count) + '</p>'
				 + '<p style="color:blue;font-size:120%\">reopen数：' + str(reopen_count) + '</p>'
				 + '<p style="color:blue;font-size:120%\">解 决 率（目标 93.8%） ：' + close_percentage + '</p>'
				 + '<p style="color:blue;font-size:120%\">测试通过率（目标 99%） ：' + notrepoen_percentage + '</p>')

	TABLE_TITLE = ('<table border="0" width="1300" bgcolor="#FFFFFF" align="left">\r\n'
					  + ' <tr>\r\n'
					  + '  <th colspan=' + str(typecount)+ ' height=40 bgcolor="#F5DEB3" >海信90天JIRA未解决问题</th>\r\n'
					  + ' </tr>\r\n')
	TABLE_LINE = (' <tr>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">JIRA ID</th>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">等级</th>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">状态</th>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">创建时间</th>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">处理人</th>\r\n'
					  + '  <th bgcolor="#CEFFCE" height=30 align="left">摘要</th>\r\n'
					  + ' </tr>\r\n')

#reopen数据独立一个表
	if reopen_count != 0:
		REOPEN_TABLE_TITLE = ('<table border="0" width="1300" bgcolor="#FFFFFF" align="left">\r\n'
							  + ' <tr>\r\n'
							  + '  <th colspan=' + str(typecount)+ ' height=40 bgcolor="#F5DEB3" >REOPEN 数据</th>\r\n'
							  + ' </tr>\r\n')
		REOPEN_TABLE_TEXT = ""
		item = 0
		for index in range(0, open_count):
			if str(JIRA_DATA[item * typecount + 2]) == "Reopened":
				bgcolor = "#FFE6D9"  # 红色
				REOPEN_TABLE_TEXT = (REOPEN_TABLE_TEXT + ' <tr>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 0]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 1]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 2]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 3]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 4]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 5]) + '</td>\r\n'
									 + ' <tr>\r\n')
			item = item + 1
		REOPEN_TABLE_TEXT = (REOPEN_TABLE_TEXT + ' <tr>\r\n' + '  <td height=40 align="left"\">' + " " + '</td>\r\n')
		REOPEN_TABLE_HTML = ('<br />\r\n'
							 + REOPEN_TABLE_TITLE
							 + TABLE_LINE
							 + REOPEN_TABLE_TEXT
							 + '</table>\r\n'
							 + '<br />\r\n')
	else:
		REOPEN_TABLE_HTML = '<br />\r\n'

#审批中数据独立一个表
	if review_count != 0:
		REVIEW_TABLE_TITLE = ('<table border="0" width="1300" bgcolor="#FFFFFF" align="left">\r\n'
							  + ' <tr>\r\n'
							  + '  <th colspan=' + str(typecount)+ 'height=40 bgcolor="#F5DEB3" >审批中数据</th>\r\n'
							  + ' </tr>\r\n')
		REVIEW_TABLE_TEXT = ""
		item = 0
		for index in range(0, open_count):
			if str(JIRA_DATA[item * typecount + 2]) == "审批中":
				bgcolor = "#FFE6D9"  # 红色
				REVIEW_TABLE_TEXT = (REVIEW_TABLE_TEXT + ' <tr>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 0]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 1]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 2]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 3]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 4]) + '</td>\r\n'
									 + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 5]) + '</td>\r\n'
									 + ' <tr>\r\n')
			item = item + 1
		REVIEW_TABLE_TEXT = (REVIEW_TABLE_TEXT + ' <tr>\r\n' + '  <td height=40 align="left"\">' + " " + '</td>\r\n')
		REVIEW_TABLE_HTML = ('<br />\r\n'
							 + REVIEW_TABLE_TITLE
							 + TABLE_LINE
							 + REVIEW_TABLE_TEXT
							 + '</table>\r\n'
							 + '<br />\r\n')
	else:
		REVIEW_TABLE_HTML = '<br />\r\n'

#其他JIRA数据独立一个表
	if other_count != 0:
		OTHER_TABLE_TITLE = ('<table border="0" width="1300" bgcolor="#FFFFFF" align="left">\r\n'
							  + ' <tr>\r\n'
							  + '  <th colspan=' + str(typecount)+ 'height=40 bgcolor="#F5DEB3" >其它非常规测试问题</th>\r\n'
							  + ' </tr>\r\n')
		OTHER_TABLE_TEXT = ""
		item = 0
		for index in range(0, other_count):
			bgcolor = "#FFE6D9"  # 红色
			OTHER_TABLE_TEXT = (OTHER_TABLE_TEXT + ' <tr>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 0]) + '</td>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 1]) + '</td>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 2]) + '</td>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 3]) + '</td>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 4]) + '</td>\r\n'
							  + '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(OTHER_JIRA_DATA[item * typecount + 5]) + '</td>\r\n'
							  + ' <tr>\r\n')
			item = item + 1
		OTHER_TABLE_TEXT = (OTHER_TABLE_TEXT + ' <tr>\r\n' + '  <td height=40 align="left"\">' + " " + '</td>\r\n')
		OTHER_TABLE_HTML = ('<br />\r\n'
							 + OTHER_TABLE_TITLE
							 + TABLE_LINE
							 + OTHER_TABLE_TEXT
							 + '</table>\r\n'
							 + '<br />\r\n')
	else:
		OTHER_TABLE_HTML = '<br />\r\n'


#open 数据表
	TABLE_TEXT = ""
	item = 0
	for index in range(0, open_count):
		if str(JIRA_DATA[item * typecount + 1]) == "Major":
			bgcolor = "#FFE6D9" #红色
		elif str(JIRA_DATA[item * typecount + 1]) == "Critical":
			bgcolor = "#FF3366"  # 大红色
		elif str(JIRA_DATA[item * typecount + 1]) == "Normal":
			bgcolor = "#EOFFFF" #蓝色
		else:
			bgcolor = "#FCFCFC" #白色
		TABLE_TEXT = (TABLE_TEXT + ' <tr>\r\n'
						+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 0]) + '</td>\r\n'
				 		+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 1]) + '</td>\r\n'
						+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 2]) + '</td>\r\n'
						+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 3]) + '</td>\r\n'
						+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 4]) + '</td>\r\n'
						+ '  <td bgcolor=' + str(bgcolor) + ' height=25 align="left"\">' + str(JIRA_DATA[item * typecount + 5]) + '</td>\r\n'
						+ ' <tr>\r\n')
		item = item + 1

	TABLE_TEXT = (TABLE_TEXT + ' <tr>\r\n' + '  <td height=40 align="left"\">' + " " + '</td>\r\n')
	OPEN_TABLE_HTML = ('<br />\r\n'
					   	+ TABLE_TITLE
					 	+ TABLE_LINE
					 	+ TABLE_TEXT
					 	+ '</table>\r\n'
					 	+ '<br />\r\n')


	htmljira_texts = ('<body>\r\n'
					  + MAIL_TITAL
					  + '<br />\r\n'
					  + MAIL_TEXT1
					  + '<br />\r\n'
					  + REOPEN_TABLE_HTML
					  + REVIEW_TABLE_HTML
					  + OPEN_TABLE_HTML
					  + OTHER_TABLE_HTML
					  + '</body>\r\n')

#将构建的邮件html备份到本地
	f = open(pathname+"/html.xml", "w")
	print(htmljira_texts, file=f)
	f.close()

#邮件配置，准备发送
	message = MIMEText(htmljira_texts, 'html')

	# 配置接收人和发送人
	sender = mail_sender
	receivers = mail_receivers
	PASSWD=mail_password

	# 发件人
	message['From'] = Header("海信JIRA数据提醒",'utf-8')

	# 收件人
	message['To'] = Header(receivers)

	# 主题
	Subject = '海信JIRA 90 天数据'
	message['Subject'] = Header(Subject, 'utf-8')

	try:
		smtpObj = smtplib.SMTP()
		smtpObj.connect('smtp.cvte.com')
		smtpObj.login(sender, PASSWD)
		smtpObj.sendmail(sender, receivers.split(','), message.as_string())
		smtpObj.quit()
		print("邮件发送成功")
	except smtplib.SMTPException:
		print("Error: 无法发送邮件")

if __name__ == '__main__':

	p1 = re.compile(r'["](.*?)["]', re.S)
	with open("Jira_data.txt", 'r', encoding='UTF-8') as f:
		for line in f.readlines():
			if "jira_server=" in line:
				strlist = line.split("jira_server=")
				jira_server = "".join(re.findall(p1, strlist[1]))

			elif "jira_user=" in line:
				strlist = line.split("jira_user=")
				jira_user = "".join(re.findall(p1, strlist[1]))

			elif "jira_password=" in line:
				strlist = line.split("jira_password=")
				jira_password = "".join(re.findall(p1, strlist[1]))

			elif "open_jira=" in  line:
				strlist = line.split("open_jira=")
				open_jira = "".join(re.findall(p1, strlist[1]))

			elif "total_jira=" in  line:
				strlist = line.split("total_jira=")
				total_jira = "".join(re.findall(p1, strlist[1]))

			elif "other_jira=" in  line:
				strlist = line.split("other_jira=")
				other_jira = "".join(re.findall(p1, strlist[1]))

			elif "mail_sender=" in  line:
				strlist = line.split("mail_sender=")
				mail_sender = "".join(re.findall(p1, strlist[1]))

			elif "mail_password=" in  line:
				strlist = line.split("mail_password=")
				mail_password = "".join(re.findall(p1, strlist[1]))

			elif "mail_receivers=" in  line:
				strlist = line.split("mail_receivers=")
				mail_receivers = "".join(re.findall(p1, strlist[1]))

			elif "week=" in  line:
				strlist = line.split("week=")
				run_week = "".join(re.findall(p1, strlist[1]))

			elif "data=" in  line:
				strlist = line.split("data=")
				run_data = "".join(re.findall(p1, strlist[1]))

		f.close()

#拦截
	today = arrow.now()
	DATE = int(today.format("DD"))
	WEEK = datetime.datetime.now().weekday()+1

	run_datalist = run_data.split(",")
	if str(WEEK) in run_week:
		print("in week data")
	elif str(DATE) in run_datalist:
		print("in data data")
	else:
		exit(0)

#时间设置

	if DATE <= 10:
		end_time = today.shift(months=+0).format("YYYY-MM-01")
		start_time = today.shift(months=-3).format("YYYY-MM-01")
	else:
		end_time = today.shift(months=+1).format("YYYY-MM-01")
		start_time = today.shift(months=-2).format("YYYY-MM-01")

	jira_data = " AND created >= " + start_time + " AND " + "created < " + end_time
	open_jira = re.sub(" ORDER BY", jira_data + " ORDER BY", open_jira)
	other_jira = re.sub(" ORDER BY", jira_data + " ORDER BY", other_jira)
	total_jira = re.sub(" ORDER BY", jira_data + " ORDER BY", total_jira)

	SendEmail()
