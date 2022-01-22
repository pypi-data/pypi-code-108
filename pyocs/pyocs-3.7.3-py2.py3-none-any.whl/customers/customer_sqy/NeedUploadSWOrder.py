#! /usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
PROJ_HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILE_PATH = os.path.dirname(os.path.abspath(__file__))
print(PROJ_HOME_PATH)
print(FILE_PATH)
LogfileDailypath=FILE_PATH + "/NeedUploadOCSOrder.txt"
sys.path.insert(1,PROJ_HOME_PATH)
sys.path.insert(2,FILE_PATH)


import re
import time
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

#=========================================================
#==================== 需要客制化的参数 ====================
#=========================================================
#客户邮箱后缀
c_mail_surffix     = r"@qiyue.cn"
#用以匹配OCS摘要中的客户订单号
c_order_id_pattern = r'[，,](\w+)\/\w+\/'
#发件人
sender = 'zhanghonghai@cvte.com'
#收件人
receivers = sender
#抄送人
Cc = sender + ',' + sender

from pyocs.pyocs_list import PyocsList
from pyocs.pyocs_software import PyocsSoftware
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_login import PyocsLogin


pop3_server = 'pop.cvte.com'
poplib._MAXLINE=20480

email_user = PyocsLogin().get_account_from_json_file()['Username'] + "@cvte.com"
password   = PyocsLogin().get_account_from_json_file()['Password']


'''
# 解析有必要的一些字符转换
'''
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


'''
# 从最新的500封邮件中检索客户邮件
'''
def get_customer_mail(c_mail_surffix):
    # 连接到POP3服务器,有些邮箱服务器需要ssl加密，可以使用poplib.POP3_SSL
    try:
        telnetlib.Telnet('pop.cvte.com', 995)
        server = poplib.POP3_SSL(pop3_server, 995, timeout=500)
    except:
        time.sleep(5)
        server = poplib.POP3(pop3_server, 110, timeout=500)

    # 身份认证:
    server.user(email_user)
    server.pass_(password)
    # 返回邮件数量和占用空间
    # print('Messages: %s. Size: %s' % server.stat())
    # list()返回所有邮件的编号:
    resp, mails, octets = server.list()
    new_email_num = len(mails)
    # print("当前邮件个数 ="+str(new_email_num))

    c_mail_info_dict = {
    'mail_summary': '',
    'mail_sender' : ''
    }
    
    c_mail_list = list()

    for index in range(new_email_num,new_email_num-500,-1):
        resp, lines, octets = server.retr(index)
        # lines存储了邮件的原始文本的每一行
        # 邮件的原始文本:
        msg_content = b'\r\n'.join(lines).decode('utf-8','ignore')
        msg = Parser().parsestr(msg_content)

        #邮件发送人
        mail_sender_pattern = re.compile('\w+[\.\w]*@\w+[\.\w]+')#匹配邮箱
        try:
            mail_sender_str = mail_sender_pattern.findall(msg.get('From',''))[0]
        except IndexError:
            continue

        if c_mail_surffix in mail_sender_str:
            c_mail_info_dict['mail_sender']  = mail_sender_str
            c_mail_info_dict['mail_summary'] = decode_str(msg.get('Subject',''))
            c_mail_list.append(c_mail_info_dict.copy())
    #关闭连接
    server.quit()
    return c_mail_list

def send_email():

    if os.access(LogfileDailypath, os.F_OK):
        fp=open(LogfileDailypath,"r")
        mail_texts=fp.read()
        fp.close()
    else:
        print("找不到文件：NeedUploadOCSOrder.txt !!! \n")
        return

    message = MIMEText(mail_texts, 'plain')
    #发件人
    message['From'] = Header(sender)
    #收件人
    message['To'] =  Header(receivers)
    #抄送人
    message['Cc'] =  Header(Cc)
    #主题
    Subject = '《可上传软件OCS订单》'+time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(sender, password) #邮箱账号
        smtpObj.sendmail(sender, receivers.split(',')+Cc.split(','), message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

'''
# 删除当天的日志文件
'''
def DeleteDailylog():
    if os.access(LogfileDailypath, os.F_OK):
        os.remove(LogfileDailypath)
    else:
        pass

def get_customer_order_id(re_pattern,src):
    ret = ''
    try :
       ret = re.search(re_pattern,src).group(1)
    except:
        return ''
    else:
        return ret

def get_searchid():
    advanced_search = {
    "0":{"search_field_name":"Task.sw_user_id","search_field_id":"555","search_field_type":"19",
        "search_field_rel_obj":"Users","search_opr":"TDD_OPER_MYSELF",
        "input1":"","input2":'null',"offset":'null'},
    "1":{"search_field_name":"Task.status","search_field_id":"584","search_field_type":"19",
        "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_EQUAL",
        "input1":"待录入需求","input2":'null',"offset":'null'},
    "2":{"search_field_name":"Task.subject","search_field_id":"554","search_field_type":"5",
        "search_field_rel_obj":"null","search_opr":"TDD_OPER_INC",
        "input1":"启悦","input2":'null',"offset":'null'}
    }
    condition = "1 and 2 and 3"
    searchid = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
    return searchid

def get_ocs_list(searchid):
    page = 1
    ocs_list = []
    while True:
        (count_tmp,list_tmp) = PyocsList().get_ocs_id_list(str(searchid) + "/page:" + str(page))
        if count_tmp == 0:
            break
        ocs_list = ocs_list + list_tmp
        page = page + 1
    return ocs_list

'''
获取OCS上 "待录入需求" 状态的订单
'''
def get_untreated_order():
    searchid = get_searchid()
    my_ocs_list = get_ocs_list(searchid)
    ocs_untreated_list = list()

    for ocs_id in my_ocs_list:
        ocs_request = PyocsDemand(ocs_id)
        current_ocs_summary = ocs_request.get_summary()
        c_order_id = get_customer_order_id(c_order_id_pattern,current_ocs_summary)
        ocs_untreated_list.append({'ocs_id':ocs_id,'c_order_id':c_order_id})

    return ocs_untreated_list


if __name__ == "__main__":

    DeleteDailylog()
    c_mail_list = get_customer_mail(c_mail_surffix)
    ocs_untreated_list = get_untreated_order()

    #针对新订单，检索客户邮件
    need_to_upload_sw_order_list = list()
    for ocs_order in ocs_untreated_list:
        for c_mail in c_mail_list:
            if ocs_order['c_order_id'] != '':
                if ocs_order['c_order_id'] in c_mail['mail_summary']:
                    need_to_upload_sw_order_list.append(ocs_order.copy())
                    break

    #将检索出来的订单写入文件中待用
    if len(need_to_upload_sw_order_list) > 0:
        fd = open(LogfileDailypath, 'w+',encoding='utf-8',errors='ignore')
        for i in need_to_upload_sw_order_list:
            msg_text = "订单号：" + i['c_order_id'] + " http://ocs.gz.cvte.cn/tv/Tasks/view/range:my/" + str(i['ocs_id']) + " 客户已发需求\n"
            fd.write(msg_text)
        fd.close()
        send_email()
    else:
        print("未检索到符合条件的订单~")