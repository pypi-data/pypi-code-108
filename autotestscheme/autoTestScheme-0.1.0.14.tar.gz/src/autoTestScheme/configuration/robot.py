import json
import hashlib
import base64
import time

import urllib3
urllib3.disable_warnings()
import requests
import datetime
import time
from Crypto.Cipher import AES
from ..common import logger


class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b"".decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s) - 1:])]

    def decrypt(self, enc):
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def decrypt_string(self, enc):
        enc = base64.b64decode(enc)
        return self.decrypt(enc).decode('utf8')


class LarkMsg(object):

    def get_feishu_report_data(self, title, created_at, duration, env, summary, is_at_all=False, at_list=[],
                         other_elements=[], button_config=[], remarks=None):
        """
        获取飞书报告模板
        :param title:
        :param created_at:
        :param duration: 
        :param env: 环境配置
        :param summary:
        :param is_at_all: 是否@所有人
        :param at_list:
        :param other_elements: 其他元素
        :param button_config: 按钮配置
        :param remarks: 备注
        :return:
        """
        header = {"title": {"tag": "plain_text", "content": title}, "template": "orange"}
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
            elements.append({"tag": "div", "fields": fields_tmp,
                             "text": {"tag": "lark_md", "content": "**{}**".format(element['title'])}})

        button = {"actions": [], "tag": "action"}
        for i in button_config:
            button['actions'].append({"tag": "button", "text": {"content": i[0], "tag": "lark_md"},
                                      "url": i[1], "type": "default", "value": {}})
        elements.append(button)
        if is_at_all is True:
            elements.append({"tag": "markdown", "content": "<at id=all></at>"})
        elif len(at_list) > 0:
            content = ""
            for user in at_list:
                content += "<at "
                if user.get('user_id') is not None:
                    content += "id='{}'".format(user.get('user_id'))
                content += " >"
                if user.get('user_name') is not None:
                    content += " {} ".format(user.get('user_name'))
                content += "</at>"
            elements.append({"tag": "markdown", "content": content})
        elements.append({"tag": "note", "elements": [{"tag": "img", "img_key": "img_b656a1a9-e63a-4795-8aa5-9e32d59eebah",
                            "alt": {"tag": "plain_text", "content": "图片"}}, {"tag": "plain_text", "content": remarks}]})
        data = {}
        data["msg_type"] = "interactive"
        config = {"wide_screen_mode": True, "enable_forward": True}
        data['card'] = {'config': config, 'elements': elements, 'header': header}
        return data

    def get_message(self, title, text):
        data = {}
        data["msg_type"] = "interactive"
        config = {"wide_screen_mode": True, "enable_forward": True}
        header = {"title": {"tag": "plain_text", "content": title}, "template": "orange"}
        elements = []
        elements.append({"tag": "div", "text": {"content": f"**😘 {text}**", "tag": "lark_md"}})
        data['card'] = {'config': config, 'elements': elements, 'header': header}
        return data

    def get_post(self, title, text):
        return {
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


class LarkSheet(object):

    def __init__(self, client, token, sheet_id=None):
        self.client = client
        self.spreadsheetToken = token
        self.sheet_id = sheet_id

    def edit_sheet(self, name, data=None, method="POST"):
        return self.client.edit_sheet(self.spreadsheetToken, name, data, method)

    def append_sheet(self, *titles):
        """
        添加sheet
        :param titles: 多个标题
        :return: 返回各个sheet_id
        """
        requests = [{'addSheet': {"properties": {"title": title, "index": index}}} for index, title in enumerate(titles)]
        response = self.edit_sheet("sheets_batch_update", {'requests': requests}).json()
        return [i["addSheet"]['properties']['sheetId'] for i in response['data']['replies']]

    def append_row(self, sheet_id, *values, style={}):
        """
        添加行
        :param values: 每一列的数据
        :param style: 样式，见https://open.larksuite.com/document/ukTMukTMukTM/ukjMzUjL5IzM14SOyMTN页样式说明
        :return:
        """
        data = {"valueRange": {"range": sheet_id, "values": [i for i in values]}}
        response = self.edit_sheet("values_append", data).json()
        _range = response['data']['tableRange']
        if len(style) > 0:
            self.set_style(_range, style)
        return _range

    def set_style(self, range, style):
        data = {"appendStyle":{"range":range,"style":style}}
        return self.edit_sheet("style", data, method="PUT").json()

    def dimension_range(self, sheet_id, end_index, size=None, start_index=1, other_type="COLUMNS", visible=True):
        """
        更新隐藏行列、单元格大小
        :param sheet_id:
        :param endindex: 结束位置
        :param size: 长度、或高度，other_type为COLUMNS时为长度，ROWS的时候为高度
        :param start_index:开始位置，默认为1
        :param other_type:默认 ROWS ，可选 ROWS（行）、COLUMNS（列）
        :param visible: 是否隐藏
        :return:
        """
        data = {"dimension":{"sheetId": sheet_id, "majorDimension": other_type, "startIndex": start_index,
                             "endIndex": end_index}, "dimensionProperties": {"visible": visible}}
        if size is not None:
            data['dimensionProperties']['fixedSize'] = size
        return self.edit_sheet("dimension_range", data, method="PUT").json()


class LarkApi(object):

    headers = {}
    is_app = True
    url = 'https://open.larksuite.com'

    def __init__(self, app_id=None, app_secret=None, access_token=None, secret=None, chat_id=None, kwargs=None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token
        self.chat_id = chat_id
        self.secret = secret
        if access_token is not None:
            self.is_app = False
        self.msg = LarkMsg()
        self.kwargs = kwargs

    def get_sheet_object(self, spreadsheetToken):
        return LarkSheet(self, spreadsheetToken)

    def send_post_message(self, title, text):
        """
        发送post信息
        :param title: 标题
        :param text: 内容
        :return:
        """
        return self.send_message(self.msg.get_message(title, text))

    def send_message(self, data):
        """
        发送消息
        :param data:
        :return:
        """
        if self.is_app is True:
            return self.send_message_by_app(self.chat_id, data)
        return self.send(data)

    def send_report(self, *args, **kwargs):
        """
        发送报告
        :param title: 标题
        :param created_at: 创建时间
        :param duration: 总用时
        :param env: 环境
        :param summary: 用例执行情况
        :param is_at_all: 是否@所有人
        :param at_list: @列表
        :return:
        """
        data = self.msg.get_feishu_report_data(*args, **kwargs)
        return self.send_message(data)

    def send_by_app(self, method, path, data=None, _json=None, params=None, is_app=True):
        headers = {'Content-Type': 'application/json'}
        if is_app is True:
            headers['Authorization'] = "Bearer " + self.get_tenant_access_token()
        url = self.url + path
        response = requests.request(method, url, params=params, headers=headers, data=json.dumps(data), json=_json,
                                verify=False)
        logger.debug(f"url:{url}, \ndata:{data}, \nheaders:{headers}, params:{params}, \nresponse:{response.text}\n")
        return response

    def send(self, data):
        """
        发送请求--群机器人
        :param data:
        :return:
        """
        return self.send_by_app("POST", "/open-apis/bot/v2/hook/" + self.access_token, data=data)

    def get_tenant_access_token(self):
        """
        获取企业自建机器人token
        :return:
        """
        if 'tenant_access_token' not in self.headers or time.time() - self.headers['time'] > self.headers['expire'] - 60:
            path = "/open-apis/auth/v3/tenant_access_token/internal"
            data = {"app_id": self.app_id, "app_secret": self.app_secret}
            response = self.send_by_app("POST", path, data, is_app=False).json()
            self.headers['expire'] = response['expire']
            self.headers['time'] = time.time()
            self.headers['tenant_access_token'] = response['tenant_access_token']
        return self.headers.get("tenant_access_token")

    def edit_sheet(self, spreadsheetToken, name, data=None, method="POST"):
        """
        编辑sheet
        :param spreadsheetToken: sheet的token，url最后一个/后面的内容
        :param name: sheets_batch_update:批量修改sheets（需要注意sheet需要进行共享编辑权限）
        :param data: data入参见https://open.larksuite.com/document/ukTMukTMukTM/uYTMzUjL2EzM14iNxMTN
        :return:
        """
        path = '/open-apis/sheets/v2/spreadsheets/{}/{}'.format(spreadsheetToken, name)
        return self.send_by_app(method, path, data, json)

    def get_feishu_decrypt(self, encrypt):
        """
        解析飞书密文
        :param encrypt:
        :return:
        """
        cipher = AESCipher("ISssDVj1umctCSYH63Xf6brcWa38nWtR")
        result = json.loads(cipher.decrypt_string(encrypt))
        return result

    def send_message_by_app(self, chat_id, req_body):
        """
        发送消息--企业自建应用
        :param chat_id:
        :param req_body:
        :return:
        """
        params = {'receive_id_type': 'chat_id'}
        req_body['receive_id'] = chat_id
        if req_body['msg_type'] == 'interactive':
            req_body['content'] = json.dumps(req_body['card'])
        elif req_body['msg_type'] == 'post':
            req_body['content'] = json.dumps(req_body['content']['post'])
        return self.send_by_app("POST", "/open-apis/im/v1/messages", data=req_body, params=params)


# sheet = LarkSheet("cli_a16d3c7ceb78d00a", "P4ntQsQ3L2c8MXPT1cRXtgVGoEk0iBLf", )
#
# robot = LarkApi("cli_a16d3c7ceb78d00a", "P4ntQsQ3L2c8MXPT1cRXtgVGoEk0iBLf")
# sheet = robot.get_sheet_object("shtusX0gWFaNl4YZOatQQyN2VSe")
# for sheet_id in sheet.append_sheet("测试4"):
#     logger.debug(sheet.append_row(sheet_id, ["标题", "时间", "test1"], ["123", "4", "56"]))
#     logger.debug(sheet.append_row(sheet_id, ["标题", "时间", "test1"], ["123", "4", "56"]))
