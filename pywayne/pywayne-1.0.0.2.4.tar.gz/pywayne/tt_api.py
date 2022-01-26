# !/usr/bin/env python
# -*- coding:utf-8 -*-
""" 
@author: Wang Ye (Wayne)
@file: tt_api.py
@time: 2021/05/29
@contact: wangye@oppo.com
@site: 
@software: PyCharm
# code is far away from bugs.
"""

import collections
import requests
import socket
from hashlib import md5
from datetime import datetime
from urllib.parse import urljoin

import hashlib
import requests
import json
from datetime import datetime
from typing import List, Dict


def _check_legal(to_users: list, check_legal=True):
    if check_legal and not (set(to_users) <= set([
        '80301815',  # *也
        '80259662',  # *威
        '80262036',  # *然
        '80261315',  # *栋
        '80264423',  # *鹏
        '80262105',  # *泽
        '80301172',  # *洲
        '80338012',  # *迪
        '80352405',  # *辰
    ])):
        raise ValueError(f'Cannot send messages to chosen users: {to_users}')


class TT_API:
    def __init__(self, to_users=[], from_user='health-algorithm', check_legal=True):
        self._appid = from_user
        self._secret = {
            'health-algorithm': '223d0590a25a47cea1385197ad31ad81',
            'health-data': '7c77496167924d4e9581d44c7dc8987a'
        }[from_user]
        self._host = 'https://ttapi.myoas.com'
        self._headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Response-Type": "application/json"
        }
        self._to_users = to_users
        self._check_legal = check_legal

    def __sign(self, path: str, payload: dict) -> str:
        flag = "_tt_"
        params_list = [path]
        payload_sorted = collections.OrderedDict(sorted(payload.items()))
        list(map(lambda x: params_list.append(x[0] + "=" + str(x[1])), payload_sorted.items()))
        params_list.append(self._secret)
        result = f"{flag}".join(params_list)
        # print(f"待签名字符串: {result}")
        return md5(result.encode('utf-8')).hexdigest()

    def send_text(self, content: str, to_users=[]):
        if to_users:
            self._to_users = to_users
        _check_legal(self._to_users, self.check_legal)
        api_path = '/s/api/message/notification/send'
        payload = {
            'appid': self._appid,
            'time': int(datetime.now().timestamp()),
            'from_user': self._appid,
            'to_users': ','.join(self._to_users),
            'msg_content': f'[{socket.gethostname()}]: {content}',
            'msg_type': '1'
        }
        payload.update({
            'sign': self.__sign(api_path, payload)
        })
        resp = requests.post(url=urljoin(self._host, api_path), headers=self._headers, data=payload)
        # print(resp.text)
        return resp


class TT_API_2:
    def __init__(self, to_users=[], from_user='health-algorithm', check_legal=True):
        self.url = r'https://mtp.myoas.com/pubacc/pubsend'
        # self.url = r'https://mtp-test.myoas.com/pubacc/pubsend  '
        self.no = '16110501'
        # self.no = '2021042801'
        self.pub = f'XT-{from_user}'
        self.pubsecret = {
            'XT-health-algorithm': 'e1cea03dc956e59a974e050e466836dd',
            'XT-health-data': 'cf129cb127bd26176b51ebb778790984'
        }[self.pub]
        self.to_users = to_users
        self.check_legal = check_legal
        self.time = 0
        self.nonce = ''
        self.pubtoken = ''
        self.body = {
            'from': {
                'no': self.no,
                'nonce': self.nonce,
                'pub': self.pub,
                'pubtoken': self.pubtoken,
                'time': self.time
            },
            'to': [
                {
                    'no': self.no,
                    'user': [
                        ''
                    ] if not self.to_users else self.to_users,
                    'code': ''
                }
            ],
            'type': 0,
            'msg': {
            }
        }

    def _set_base_body(self):
        self.body['from']['time'] = self._get_current_time()
        self.body['from']['nonce'] = str(self.body['from']['time'])
        self.body['from']['pubtoken'] = self._get_pubtoken(
            no=self.no,
            time=self.body['from']['time'],
            nonce=self.body['from']['nonce'],
            pubsecret=self.pubsecret,
            pub=self.pub
        )

    def _get_pubtoken(self, no, time, nonce, pubsecret, pub):
        def get_str_sha1_secret_str(res):
            sha = hashlib.sha1(res.encode('utf-8'))
            encrypts = sha.hexdigest()
            return encrypts

        list_temp = []
        list_temp.append(str(no))
        list_temp.append(str(time))
        list_temp.append(str(nonce))
        list_temp.append(str(pubsecret))
        list_temp.append(str(pub))
        list_temp.sort()

        str_temp = ''.join(list_temp)
        pubtoken = get_str_sha1_secret_str(str_temp)
        return pubtoken

    def _get_current_time(self):
        return int(datetime.now().timestamp() * 1000)

    def _post_request(self):
        header = {
            'Content-Type': 'application/json'
        }
        # import pprint
        # pprint.pprint(self.body)
        req = requests.post(self.url, data=json.dumps(self.body), headers=header)
        # print(req.status_code)

    def send_text(self, msg_text: str, to_users=[]):
        self._set_base_body()
        if to_users:
            self.body['to'][0]['user'] = to_users
        else:
            self.body['to'][0]['user'] = self.to_users
        _check_legal(self.body['to'][0]['user'], self.check_legal)
        self.body['to'][0]['code'] = '2'
        self.body['type'] = 2
        self.body['msg']['text'] = f'[{socket.gethostname()}]: {msg_text}'
        self._post_request()

    def send_text_with_url(self, msg_text: str, to_url='', to_users=[]):
        self._set_base_body()
        if to_users:
            self.body['to'][0]['user'] = to_users
        else:
            self.body['to'][0]['user'] = self.to_users
        _check_legal(self.body['to'][0]['user'], self.check_legal)
        self.body['to'][0]['code'] = '2'
        self.body['type'] = 5
        self.body['msg'] = {
            'text': msg_text,
            'url': to_url,
            'appid': '100000',
            'todo': 0,
            'sourceid': '',
            'device': 0,
            'urlMb': to_url,  # 'http://www.zhihu.com/',
            'urlPc': to_url,  # 'http://www.bing.com/'
        }
        self._post_request()

    def send_pic_text_single_text(self, msg_title: str, msg_text: str, to_url='', to_users=[]):
        self._set_base_body()
        if to_users:
            self.body['to'][0]['user'] = to_users
        else:
            self.body['to'][0]['user'] = self.to_users
        _check_legal(self.body['to'][0]['user'], self.check_legal)
        self.body['to'][0]['code'] = '2'
        self.body['type'] = 6
        self.body['msg'] = {
            'sourceid': '',
            'todo': 0,
            'model': 1,
            'list': [
                {
                    'text': msg_text,
                    'title': msg_title,
                    # 'date': str(datetime.now()),
                    # 'zip': 'URLENCODE'
                }
            ]
        }
        if to_url:
            self.body['msg']['list'][0].update({
                'device': 0,
                'urlMb': to_url,
                'urlPc': to_url,
            })
        self._post_request()

    def send_pic_text_single_text_pic(
            self, msg_text: str, msg_title: str,
            pic_name: str, pic_base64: str, to_url='', to_users=[]
    ):
        self._set_base_body()
        if to_users:
            self.body['to'][0]['user'] = to_users
        else:
            self.body['to'][0]['user'] = self.to_users
        _check_legal(self.body['to'][0]['user'], self.check_legal)
        self.body['to'][0]['code'] = '2'
        self.body['type'] = 6
        self.body['msg'] = {
            'sourceid': '',
            'todo': 0,
            'model': 2,
            'list': [
                {
                    'text': msg_text,
                    'title': msg_title,
                    # 'date': str(datetime.now()),
                    'name': pic_name,
                    'pic': pic_base64,
                    # 'zip': 'URLENCODE'
                }
            ]
        }
        if to_url:
            self.body['msg']['list'][0].update({
                'device': 0,
                'urlMb': to_url,
                'urlPc': to_url,
            })
        self._post_request()

    def send_pic_text_multi_text_pic(
            self, msg_content: List[Dict[str, str]], to_users=[]
    ):
        self._set_base_body()
        if to_users:
            self.body['to'][0]['user'] = to_users
        else:
            self.body['to'][0]['user'] = self.to_users
        _check_legal(self.body['to'][0]['user'], self.check_legal)
        self.body['to'][0]['code'] = '2'
        self.body['type'] = 6
        self.body['msg'] = {
            'sourceid': '',
            'todo': 0,
            'model': 3,
            'list': []
        }
        for mc in msg_content:
            self.body['msg']['list'].append({
                'title': mc['title'],
                'name': mc['name'],
                'pic': mc['pic']
            })
            if 'url' in mc and mc['url']:
                self.body['msg']['list'][-1].update({
                    'device': 0,
                    'urlMb': mc['url'],
                    'urlPc': mc['url']
                })
        self._post_request()

    @staticmethod
    def get_pic_base64(img_path):
        import base64
        with open(img_path, 'rb') as f:
            image_data = f.read()
            base64_data = str(base64.b64encode(image_data), encoding='utf-8')  # base64编码
            # print(base64_data)
            # print(type(base64_data))
            return base64_data

    def help(self):
        print("""tt = TT_API_2()
tt.send_text('hello', ['80301815'])
tt.send_text_with_url('hello url', 'http://www.baidu.com/', ['80301815'])
tt.send_text_with_url('hello url', r'http://www.baidu.com', ['80301815'])
tt.send_pic_text_single_text('标题', '正文', 'http://www.baidu.com', ['80301815'])
pic_base64 = get_pic_base64('test.jpg')
tt.send_pic_text_single_text_pic('标题', '正文', 'my_pic.jpg', pic_base64, to_url='www.baidu.com', to_users=['80301815'])
pic_base641 = get_pic_base64('test.jpg')
pic_base642 = get_pic_base64('test2.jpg')
tt.send_pic_text_multi_text_pic(
    msg_content=[
        {
            'title': '标题1',
            'name': '正文1AAAAAAAAAAAAAAAAAAAAAAAAAAAA\naaaaaaaaaaaaa',
            'pic': pic_base641,
            'url': 'http://www.baidu.com/'
        },
        {
            'title': '标题2',
            'name': '正文2AAAAAAAAAAAAAAAAAAAAAAAAAAAA\naaaaaaaaaaaaa',
            'pic': pic_base642,
            'url': 'http://www.bing.com'
        },
        {
            'title': '标题3',
            'name': '正文3AAAAAAAAAAAAAAAAAAAAAAAAAAAA\naaaaaaaaaaaaa',
            'pic': pic_base642,
            'url': 'http://www.bing.com'
        },
        {
            'title': '标题4',
            'name': '正文4AAAAAAAAAAAAAAAAAAAAAAAAAAAA\naaaaaaaaaaaaa',
            'pic': pic_base642,
            'url': 'http://www.bing.com'
        }
    ],
    to_users=['80301815']
)
""")

