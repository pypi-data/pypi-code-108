

import os
import time
import hmac
import json
import base64
from hashlib import sha256
import requests
from autoTestScheme.common import logger
from dingtalkchatbot.chatbot import DingtalkChatbot

class Feishu(object):

    def __init__(self, access_token, secret, url="https://open.feishu.cn/open-apis/bot/v2/hook/"):
        self.access_token = access_token
        self.secret = secret
        self.url = url

    def get_url(self):
        if self.url.endswith("/") is False:
            self.url += "/"
        return self.url + self.access_token

    def send(self, data):
        headers = {'Content-Type': 'application/json'}
        url = self.get_url()
        logger.info(data)
        return requests.request("POST", url, headers=headers, data=json.dumps(data), verify=False)

    def send_message(self, title, text):
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [[{"tag": "text", "text": text}]
                        ]
                    }
                }
            }
        }
        return self.send(data)

    def get_fileds(self, _list):
        fields = []
        i = 0
        for value in _list:
            if i % 2 == 0:
                fields.append({"is_short": False, "text": {"tag": "lark_md", "content": ""}})
            fields.append(
                {"is_short": True, "text": {"tag": "lark_md", "content": "**{}**\n{}".format(value[0], value[1])}})
            i += 1
        return fields

    def send_lark_report(self, title, created_at, duration, env, summary, link, is_at_all=False, at_list=[],
                         other_elements=[]):
        """
        发送lark报告
        :param title: 标题
        :param created_at: 创建时间
        :param duration: 总用时
        :param env: 环境
        :param summary: 用例执行情况
        :param link: 报告地址
        :param is_at_all: 是否@所有人
        :param at_list: @列表
        :return:
        """
        logger.error(other_elements)
        header = {"title": {"tag": "plain_text", "content": title}, "template": "blue"}
        fields1 = self.get_fileds(env)
        fields2 = self.get_fileds([['创建时间', created_at], ['执行总时长', duration]])
        fields3_data = []
        for i in [('总用例数', 'total'), ('成功', 'passed'), ('失败', 'failed'), ('代码异常', 'broken'), ('跳过', 'skipped')
                 , ('未知', 'unknown')]:
            if summary.get(i[1]) is not None and summary.get(i[1]) > 0:
                fields3_data.append([i[0], summary.get(i[1])])
        fields3 = self.get_fileds(fields3_data)
        elements = []
        elements.append({"tag": "div", "fields": fields1, "text": {"tag": "lark_md", "content": "**环境详情**"}})
        elements.append({'tag': 'hr'})
        elements.append({"tag": "div", "fields": fields2, "text": {"tag": "lark_md", "content": "**用时详情**"}})
        elements.append({'tag': 'hr'})
        elements.append({"tag": "div", "fields": fields3, "text": {"tag": "lark_md", "content": "**执行详情**"}})
        for element in other_elements:
            elements.append({'tag': 'hr'})
            fields_tmp = self.get_fileds(element['fields'])
            elements.append({"tag": "div", "fields": fields_tmp, "text": {"tag": "lark_md", "content": "**{}**".format(element['title'])}})
        elements.append({"actions": [{"tag": "button", "text": {"content": "查看详情", "tag": "lark_md"},
                                             "url": link, "type": "default", "value": {}}], "tag": "action"})

        data = {}
        data["msg_type"] = "interactive"
        config = {"wide_screen_mode": True, "enable_forward": True}
        data['card'] = {'config': config, 'elements': elements, 'header': header}
        headers = {'Content-Type': 'application/json'}
        if self.secret != '' and self.secret is not None:
            timestamp = str(round(time.time()))
            key = '{}\n{}'.format(timestamp, self.secret)
            key_enc = key.encode('utf-8')
            hmac_code = hmac.new(key_enc, digestmod=sha256).digest()
            sign = base64.b64encode(hmac_code).decode('utf-8')
            data["timestamp"] = timestamp
            data["sign"] = sign
        data['at'] = {}
        data['at']["isAtAll"] = is_at_all
        return self.send(data)


class Robot(object):

    def __init__(self):
        pass

    def get_markdown(self, created_at, env, environment, summary, title=None, link=None, is_feishu=False):
        msg = ''
        
        if title is not None:
            msg += '## {}\n'.format(title)
            msg += '___\n'
        for i in env:
            msg += '#### <font color="#000000">{}</font><br/>{}\n'.format(i[0], i[1])
        msg += '#### <font color="#000000">创建时间:</font><br/>{}\n'.format(created_at)
        msg += '#### <font color="#000000">语言环境:</font><br/>\n'
        son1 = '' if is_feishu is True else '+ '
        for key, value in environment.items():
            msg += '{}<font color="#00FF7F">{}:</font>{}\n'.format(son1, key, value)
        msg += '#### <font color="#000000">测试结果:</font><br/>\n'
        language = {}
        language['num_tests'] = '<font color="#00FF7F">总条数:</font><br/>'
        language['passed'] = '<font color="#00FF7F">成功:</font><br/>'
        language['duration'] = '<font color="#00FF7F">执行时长(秒):</font><br/>'
        language['failed'] = '<font color="#FF0000">执行失败:</font><br/>'
        language['skipped'] = '<font color="#FFE4C4">跳过:</font><br/>'
        language['total'] = '<font color="#FFE4C4">总条数:</font><br/>'
        language['broken'] = '<font color="#FFE4C4">代码异常:</font><br/>'
        language['unknown'] = '<font color="#FFE4C4">未知:</font><br/>'
        son2 = '' if is_feishu is True else '- '
        for key, value in summary.items():
            if key in list(language.keys()):
                key = language[key]
            msg += '{}{}{}\n'.format(son2, key, value)
        if link is not None:
            msg += '#### <font color="#000000">详情</font><br/>:[点此跳转]({})'.format(link)
        return msg

    def execute_robot(self, robot_type, access_token, secret, title, created_at, env, environment, summary, link, is_at_all=False, at_list=[]):
        self.robot_type = robot_type
        self.access_token = access_token
        self.secret = secret
        self.title = title
        self.created_at = created_at
        self.env = env = env
        self.environment = environment
        self.summary = summary
        self.link = link
        self.is_at_all = is_at_all
        self.at_list = at_list
        if robot_type == 'dingtalk':
            return self.send_dingtalk(access_token, secret, title, created_at, env, environment, summary, link, is_at_all, at_list)
        elif robot_type == 'feishu_report':
            return self.send_feishu_report(access_token, secret, title, created_at, env, environment, summary, link, is_at_all, at_list)

    def send_dingtalk(self, access_token, secret, title, created_at, env, environment, summary, link, is_at_all=False, at_list=[]):
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(access_token) 
        xiaoding = DingtalkChatbot(webhook, secret=secret) # 方式二：勾选“加签”选项时使用（v1.5以上新功能） 
        msg = self.get_markdown(created_at, env, environment, summary, title, link)
        return xiaoding.send_markdown(title, msg, is_at_all=is_at_all, at_mobiles=at_list)

    def send_feishu_report(self, access_token, secret, title, created_at, env, environment, summary, link, is_at_all=False, at_list=[]):
        if 'http' in access_token:
            url = access_token
        else:
            url = 'https://open.feishu.cn/open-apis/bot/v2/hook/{}'.format(access_token)
        # data = {}
        header = {"title": {"tag": "plain_text", "content": title}, "template": "blue"}
        print(env)
        fields1 = []
        i = 0
        for value in env:
            if i % 2 == 0:
                fields1.append({"is_short": False, "text": {"tag": "lark_md", "content": ""}})
            fields1.append({"is_short": True, "text": {"tag": "lark_md", "content": "**{}**\n{}".format(value[0], value[1])}})
            i += 1
        fields2 = []
        fields2.append({"is_short": True, "text": {"tag": "lark_md", "content": "**创建时间:**\n{}".format(created_at)}})
        fields2.append({"is_short": True, "text": {"tag": "lark_md", "content": "**执行总时长:**\n{}".format(created_at)}})
        fields3 = []
        fields3.append({"is_short": False, "text": {"tag": "lark_md", "content": ""}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**总用例数:**\n{}".format(summary.get('total'))}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**成功:**\n{}".format(summary.get('passed'))}})
        fields3.append({"is_short": False, "text": {"tag": "lark_md", "content": ""}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**失败:**\n{}".format(summary.get('failed'))}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**代码异常:**\n{}".format(summary.get('broken'))}})
        fields3.append({"is_short": False, "text": {"tag": "lark_md", "content": ""}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**跳过:**\n{}".format(summary.get('skipped'))}})
        fields3.append({"is_short": True, "text": {"tag": "lark_md", "content": "**未知:**\n{}".format(summary.get('unknown'))}})
        elements = []
        elements.append({"tag": "div", "fields": fields1, "text": {"tag": "lark_md", "content": "**环境详情**"}})
        elements.append({'tag': 'hr'})
        elements.append({"tag": "div", "fields": fields2, "text": {"tag": "lark_md", "content": "**执行时间**"}})
        elements.append({'tag': 'hr'})
        elements.append({"tag": "div", "fields": fields3, "text": {"tag": "lark_md", "content": "**执行详情**"}})
        elements.append({"actions": [{"tag": "button", "text": {"content": "查看详情", "tag": "lark_md"},
                                             "url": link, "type": "default", "value": {}}], "tag": "action"})


        data = {}
        data["msg_type"] = "interactive"
        config = {"wide_screen_mode": True, "enable_forward": True}
        data['card'] = {'config': config, 'elements': elements, 'header': header}
        headers = {'Content-Type': 'application/json'}
        if secret != '' and secret is not None:
            timestamp = str(round(time.time()))
            key = '{}\n{}'.format(timestamp, secret)
            print(key)
            key_enc = key.encode('utf-8')
            hmac_code = hmac.new(key_enc, digestmod=sha256).digest()
            sign = base64.b64encode(hmac_code).decode('utf-8')
            data["timestamp"] = timestamp
            data["sign"] = sign
        data['at'] = {}
        data['at']["isAtAll"] = is_at_all
        print(url, data)
        response = requests.request("POST", url, headers=headers, data=json.dumps(data), verify=False)
        return response.text
    
    def send_feishu(self,  access_token, secret, title, text):
        headers = {'Content-Type': 'application/json'}
        if 'http' in access_token:
            url = access_token
        else:
            url = 'https://open.feishu.cn/open-apis/bot/v2/hook/{}'.format(access_token)
        data = {
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": title,
                        "content": [[{"tag": "text", "text": text}]
                        ]
                    }
                }
            }
        }
        response = requests.request("POST", url, headers=headers, data=json.dumps(data), verify=False)
        return response.text
    

robot = Robot()
