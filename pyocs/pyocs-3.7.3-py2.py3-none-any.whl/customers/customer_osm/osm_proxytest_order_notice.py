import os
import sys

PRJ_HOME_PATH = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# print(PRJ_HOME_PATH)
sys.path.insert(1,PRJ_HOME_PATH)

import re
from w3lib import html
from pyocs.pyocs_demand import PyocsDemand
from pyocs.pyocs_software import PyocsSoftware
from pyocs.pyocs_list import PyocsList
from pyocs.pyocs_login import PyocsLogin

import time
import datetime

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

"""
# @author: zhanghonghai
# @作用：可代测的订单，内勤会在订单评论区回复代测；脚本自动识别此通知代测的评论信息，并邮件通知软件工程师修改软件状态
# @className: OsmOrderNotice
"""

#需捞取订单的成员（FAE+代工）：
members = "罗仪凡 邓世琼 裘晨曦 刘瑜敏 章德余 郑永祥 江庆元 徐安奎 张仁斌 雷小军 琚陈李 邹代好 武建如 王鹏 谢澔 李阳秋 卢成帆 陈吉平 张宏海 陈潮雄 林祥纳 陈嘉艺8469 陆天等 黄淑荣 杨炳坤 孔令志 冼健荣 张立帅 陈福枢 萧植涛 黎佩龙 郑泽淼 陈讲鹏 赵溪楠 吕鋆泉 何健 邓思敏 李路 梁凯 银泽 李琨 王航 陆龙飞 李辉 谢锦财 何勋 易武进 陈家兴 何志伟 陈凡 师伟 童正伟 梁兆征 李建峤 吴海明 刘家豪"

email_user = PyocsLogin().get_account_from_json_file()['Username'] + "@cvte.com"
email_password   = PyocsLogin().get_account_from_json_file()['Password']

###
# 解析一些字符转换
###
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value

###
# 发送邮件
###
def send_email(mail_receiver,mail_text):
    mail_text_prefix = '您的如下订单，内勤已在评论区回复代测，需今天内维护好客户确认状态，谢谢。\n\n'
    mail_text_suffix = '\n\n此邮件由脚本自动发送，请勿回复，谢谢。'
    #邮件正文
    message = MIMEText(mail_text_prefix + mail_text + mail_text_suffix, 'plain')
    #发件人
    message['From'] = Header(email_user)
    #收件人
    message['To'] =  Header(mail_receiver)
    #主题
    Subject = "《代测订单处理》"+time.strftime("%Y%m%d", time.localtime())
    message['Subject'] = Header(Subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect('smtp.cvte.com')
        smtpObj.login(email_user, email_password) #邮箱账号
        smtpObj.sendmail(email_user, mail_receiver.split(','), message.as_string())
        smtpObj.quit();
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

def get_searchid():
    advanced_search = {
    "0":{"search_field_name":"Task.rel_obj_id.rel_obj_id.mf_status","search_field_id":"1637","search_field_type":"19",
        "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_NOT_INC",
        "input1":"已代测发放","input2":'null',"offset":'null'},
    "1":{"search_field_name":"Task.rel_obj_id.rel_obj_id.mf_status","search_field_id":"1637","search_field_type":"19",
        "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_NOT_INC","input1":"已最终发放","input2":'null',"offset":'null'},
    "2":{"search_field_name":"Task.status","search_field_id":"584","search_field_type":"19",
        "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_LE_EQUAL",
        "input1":"待发放","input2":'null',"offset":'null'},
    "3":{"search_field_name":"Task.account_id","search_field_id":"560","search_field_type":"19",
        "search_field_rel_obj":"Accounts","search_opr":"TDD_OPER_NOT_INC",
        "input1":"TCL","input2":'null',"offset":'null'},
    "4":{"search_field_name":"Task.account_id","search_field_id":"560","search_field_type":"19",
        "search_field_rel_obj":"Accounts","search_opr":"TDD_OPER_NOT_INC",
        "input1":"视睿","input2":'null',"offset":'null'},
    "5":{"search_field_name":"Task.sw_user_id","search_field_id":"555","search_field_type":"19",
        "search_field_rel_obj":"Users","search_opr":"TDD_OPER_INC",
        "input1":members,"input2":'null',"offset":'null'},
     "6":{"search_field_name":"Task.account_firmware_status","search_field_id":"1779","search_field_type":"19",
          "search_field_rel_obj":"Enums","search_opr":"TDD_OPER_EQUAL",
          "input1":"客户未确认","input2":'null',"offset":'null'},
    "7":{"search_field_name":"Task.subject","search_field_id":"554","search_field_type":"5",
         "search_field_rel_obj":"null","search_opr":"TDD_OPER_NOT_INC",
         "input1":"虚拟","input2":'null',"offset":'null'}
    }
    condition = "1 and 2 and 3 and 4 and 5 and 6 and 7 and 8"
    searchID = PyocsSoftware().get_searchid_from_advanced_search(advanced_search, condition)
    print(searchID)
    return searchID

def get_ocs_list_by_searchid(searchid, isSampleOrder = False):
    page = 1
    ocsList = []
    while True:
        searchidPara = str(searchid) + "/page:" + str(page)
        (count1tmp,list1tmp) = PyocsList().get_ocs_id_list(searchidPara)
        if count1tmp == 0:
            break
        ocsList = ocsList + list1tmp
        page = page + 1
    return ocsList


if __name__ == '__main__':
    #获取待处理的OCS List
    # ocs_list = ['637328','625378','636849']
    ocs_list = get_ocs_list_by_searchid(get_searchid())
    # print(ocs_list)

    proxytest_order_dict = dict()
    for ocs in ocs_list:
        r = PyocsDemand(ocs)
        #获取订单评论区信息
        comment_str = html.remove_tags(r.get_task_comment_area())
        sw_engineer = r.get_ocs_software_engineer()
        TaskCommentPattern = re.compile(r'"cmt_id.*?"type":"TaskComment"}', re.DOTALL)
        comment_list = TaskCommentPattern.findall(comment_str)

        #判断订单是否需代测：
        url = 'http://ocs-api.gz.cvte.cn/tv/Tasks/view/range:all/'
        for comment in comment_list:
            if '内勤处理结论为代测' in comment:
                if sw_engineer not in proxytest_order_dict.keys():
                    proxytest_order_dict[sw_engineer] = list()
                proxytest_order_dict[sw_engineer].append(url + ocs)
                break
    print(proxytest_order_dict)

    #获取每个工程师的邮箱地址，并邮件推送待测订单信息
    for key,value in proxytest_order_dict.items():
        sw_engineer_mail = PyocsSoftware().get_email_addr_from_ocs(key)
        send_email(sw_engineer_mail,'\n'.join(value))




