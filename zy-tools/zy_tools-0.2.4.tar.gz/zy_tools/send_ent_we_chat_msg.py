# !/usr/bin/env python
# _*_coding: utf-8 _*_
# @Time: 2020/1/22 11:30
# @Author: "John"
import json
import urllib3

import requests

urllib3.disable_warnings()


def send_msg(web_hook, content, mentioned_mobile_list=None):
    """
        发送企业微信消息，并可以 @ ，将需要被 @ 的人的 id 或者手机号放到 mentioned_mobile_list
    :param content: 发送信息内容
    :param web_hook: 指定机器人的 url
    :param mentioned_mobile_list: list, 默认为None，不指定@ 对象
    :return:
    """

    if not web_hook:
        return
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    data = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_mobile_list": mentioned_mobile_list
        }
    }
    post_data = json.dumps(data)
    requests.post(web_hook, headers=headers, data=post_data)
