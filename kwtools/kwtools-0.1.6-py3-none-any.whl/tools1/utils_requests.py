import os
import sys
from retry import retry
import traceback
import pysnooper
import user_agent
import time
import random
import requests
import re
import json
import collections
import threading   # threading.Thread 为可使用的多线程的类！
import multiprocessing # multiprocessing.Process 为可使用的多进程的类！
# from scrapy import Selector
from urllib import parse
import smtplib, uuid
from email.mime.text import MIMEText
import execjs
from copy import deepcopy
import redis
import socket
import websocket
import ssl
from kwtools.settings import logger

## exchange邮件发送相关的库包
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
# import urllib3
# urllib3.disable_warnings() # 可以避免老是报错...



class myRequest():
    def __init__(self):
        self.name = "kerwin"
        self.session = requests.Session()


    def build_parameters(self, query_dict: dict):
        """
            function: 将dict格式的query, 转化成'name=kerwin&age=27'的str格式 (便于http传递)
        """
        keys = list(query_dict.keys())
        keys.sort()
        query_str = '&'.join([f"{key}={query_dict[key]}" for key in query_dict.keys()])
        return query_str


    # 所有请求都用这个接口！
    @retry(tries=3, delay=4, backoff=2, max_delay=8) # 这里的4次retry是正常的网络连接出错重试(不考虑反爬)
    def req(self, url, *, proxies=None, selector=False, auth=None, allow_redirects=True,
            data=None, selenium=False, req_method="get", is_obj=False, use_session=False,
            sleep_sec=None, other_headers={}, timeout=30, encoding=None, requests=requests,
            **kwargs):
        """
        params:
            data: dict类型
            other_headers: dict类型
            **kwargs:
                cookies: 可传入一个dict类型的cookies_dict  (前提: other_headers中不能有"cookie")



        note:
            1.所有请求都用这个通用接口(要做到普遍性)
            2.服务器连接类型的出错,可以直接用上面的retry.不需要在robust_req中考虑了!
            3. 默认情况只返回 res_obj.text 文本 (一般需要用到res_obj对象比较少见)
            4. verify的作用是: 表明在访问https协议的网址时, 是否需要验证服务器的 server's TLS certificate. requests库默认为True.
                有时候使用charles时候在用req访问 'https网址', 会报错: 服务器tls证书验证失败, 导致的SSLError(bad handshake)
            5. requests.get() 方法是默认允许 "重定向/跳转"的!!
                    so: 当需要禁止跳转的时候, 在get()方法中加入: allow_redirects=False

        tips:  res_obj.status_code 为200时再做后续处理？
        """

        headers = {
            "User-Agent": user_agent.generate_user_agent(),
            # "Host": "www.dianping.com",
            # "Referer": "http://price.ziroom.com",
            # "Cookie": "a=123;b=456;c=789",
        }
        # 0. 如果使用session，之后302跳转过程中的所有cookies，都会存储在这个 self.session中
            ### 上面的入参 requests=requests 是避免这里把全局变量requests给屏蔽掉了
        if use_session:
            requests = self.session

        # 1.添加其他必要的头部信息(包括cookies可以以{"Cookie":"a=123;b=456;c=789"}形式update进来)
        # cookies 也可以含在other_headers里面
        headers.update(other_headers)

        # 2.使用代理ip
        if proxies is not None:
            if proxies == "abuyun":
                proxies = AbuyunProxies.proxies
            elif proxies == "clash":
                proxies = {
                    # 代理设置: 如果要翻墙, 需要把端口号改成clash的端口号
                    "http" :"http://localhost:7890",
                    "https" :"https://localhost:7890",
                    # "http" :"socks5://127.0.0.1:7890",
                    # "https" :"socks5://127.0.0.1:7890",
                }
            elif proxies == "charles":
                proxies = {
                    # 代理设置: 如果要通过charles抓取python发出请求的数据包, 需要把端口号改成charles的端口号
                    # (1. clash设置成系统代理; 即: 除本机外的第一层全局代理; 所有浏览器/软件发出的请求都先经过clash代理)
                    # (2. charles需要设置成clash外的二层代理 [external proxy]; )
                    "http" :"http://localhost:8888",
                    "https" :"https://localhost:8888",
                    # "http" :"socks5://localhost:8889",
                    # "https" :"socks5://localhost:8889",
                }
        else:
            # 默认使用不使用代理
            proxies = {
                # 代理设置: 如果要翻墙, 需要把端口号改成clash的端口号 (这里的1080是以前ssr的端口)
                # "http" :"http://localhost:1080",
                # "https" :"https://localhost:1080"

                # 需要密码认证的代理:
                # "http" :"http://user:password@ip:port",

                # 也可以用socks协议的代理:
                # "http" :"socks5://user:password@ip:port",
                # "https" :"socks5://user:password@ip:port",

                # notice: 意味着 '左边的请求' 会使用 '右边的代理' 来访问

            }

        # 3. 设置其他'关键参数'的默认值
            # 这里设置不需要SSL认证...
        kwargs.setdefault('verify', False) # [超级重要]: 对于https请求, 很多时候需要SSL认证, 有时候没有认证就请求失败...很麻烦..


        # 4.开始发送req
        # print("\nreq 已发出。。\n")
        # logger.log(logging.DEBUG, "req 已发出..\n")
        if req_method.lower() == "get":
            res_obj = requests.get(url, headers=headers,proxies=proxies, auth=auth, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        # 下面的 data参数 必须要先用json.dumps()转成str后，才能发送请求！！！ //k200628: 不需要转成json啊, 直接用dict类型就能传入请求啊 // 22年0117日: data参数直接传dict不行啊!!!还是要dumps()
        elif req_method.lower() == "post":
            res_obj = requests.post(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        elif req_method.lower() == "put":
            res_obj = requests.put(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        elif req_method.lower() == "delete":
            res_obj = requests.delete(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        else:
            msg = f"req_method未知: {req_method}; 请检查..."
            logger.error(msg)
            res_obj = None
        self.res_obj = res_obj

        # 5.修改需要的编码格式
        if encoding:
            res_obj.encoding = encoding

        # 6.当需要返回原始response对象的时候
        if is_obj:
            return res_obj
        else:
            res_text = res_obj.text

        # 7.当需要对页面进行解析的时候可以开启这段代码
        if selector:
            selector = Selector(text=res_text)
            return selector

        # 8.睡眠 (怕被反爬..)
        if sleep_sec:
            time.sleep(sleep_sec)

        # 9.返回文本string
        return res_text


    def get_cookies_from_session(self):
        # 获取整个session中的所有cookies！！好用！！ (自动解析cookiejar成dict)
        return requests.utils.dict_from_cookiejar(self.session.cookies)


    def get_cookies_from_res_obj(self):
        return requests.utils.dict_from_cookiejar(self.res_obj.cookies)



class UtilsRequests():
    def  __init__(self):
        self.req = myRequest().req


    def url_encode(self, txt):
        "url编码: 网络请求中特有'编码格式'(区别于unicode);"
        "正常来说, http/s请求的时候, 会自动把中文进行url编码; 但有时候, 需要我们手动对url进行编码, 所以写了个k接口"
        return parse.quote(txt)


    def url_decode(self, txt):
        "url解码: 把%E6%9c%88 解码成 '月' "
        return parse.unquote(txt)


    def get_my_ip(self, option=None, proxies=None):
        "用来测试服务器观测到我的请求是来自哪个ip的"
        "与代理ip相关"
        # req = myRequest().req
        req = self.req
        api_url = 'http://pv.sohu.com/cityjson?ie=utf-8'
        res_text = req(api_url, proxies=proxies)
        res_text = re.findall(r'({[\s\S]+})', res_text)[0]
        print(res_text)
        res_dict = json.loads(res_text)
        if option == "ip":
            return res_dict.get("cip")
        elif option == "name":
            return res_dict.get("cname")
        else:
            return res_dict



class AbuyunProxies():

    # 代理服务器
    proxyHost = "http-dyn.abuyun.com"
    proxyPort = "9020"

    # 代理隧道验证信息
    proxyUser = "H9E6383C4ONW1AOD"
    proxyPass = "11844987BD73DCAD"

    proxyMeta = f"http://{proxyUser}:{proxyPass}@{proxyHost}:{proxyPort}"

    proxies = {
        "http"  : proxyMeta,
        "https" : proxyMeta,
    }



utils_requests = UtilsRequests()



if __name__ == '__main__':
    pass
