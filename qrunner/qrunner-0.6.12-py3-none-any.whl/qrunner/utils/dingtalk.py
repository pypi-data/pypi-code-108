import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json


# 钉钉机器人
class Robot:
    def __init__(self, secret, url):
        self.secret = secret
        self.url = url

    # 生成时间戳timestamp和签名数据sign用于钉钉机器人的请求
    def __gen_timestamp_and_sign(self):
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.secret.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    # 发送钉钉机器人通知
    def send_msg(self, msg_data):
        # 从gen_timestamp_and_sign方法获取timestamp和sign
        timestamp, sign = self.__gen_timestamp_and_sign()
        # 机器人url
        robot_url = self.url
        # 拼接请求url
        url = '{0}&timestamp={1}&sign={2}'.format(robot_url, timestamp, sign)
        print(url)
        # 请求头
        headers = {'Content-Type': 'application/json'}
        # 发送请求
        ret = requests.post(url, headers=headers, data=json.dumps(msg_data), verify=False)
        # 判断请求结果
        ret_dict = ret.json()
        if ret_dict.get('errcode') == 0:
            print('消息发送成功')
        else:
            print('消息发送失败: {}'.format(ret_dict.get('errmsg')))


if __name__ == '__main__':
    # im测试群：im测试助手
    robot_info_default = {
        'secret': 'SECe0e8136eb7b81f712cb3b277cde794159c9ab24f3489b1d9f26629d79494403a',
        'webhook_url': 'https://oapi.dingtalk.com/robot/send?access_token=487648aceb8a9e499673307c9647c2332599'
                       'd0079a7a00c80ce5b1870b1a4b22'
    }
    r_secret = robot_info_default.get('secret')
    r_url = robot_info_default.get('webhook_url')

    # 默认消息内容
    data_default = {
        "msgtype": "markdown",
        "markdown": {
            "title": '测试',
            "text": '测试123'
        }
    }

    # 消息拼接示例
    # result_text = "### *{0}*\n\n" \
    #     "<font color=#C0C0C0>用例数：</font>{1}，" \
    #     "<font color=#C0C0C0>通过：</font><font color=#00FF00>{2}</font>，" \
    #     "<font color=#C0C0C0>失败：</font><font color=#FF0000>{3}</font>，" \
    #     "<font color=#C0C0C0>成功率：</font><font color=#00FF00>{4}%</font>\n" \
    #     "> #### [查看详情]({5})\n".format(msg_title, total, pass_num, fail_num, pass_rate, url)

    robot = Robot(r_secret, r_url)
    robot.send_msg(data_default)
