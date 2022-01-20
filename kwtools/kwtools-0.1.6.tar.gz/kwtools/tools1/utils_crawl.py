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
from scrapy import Selector
from urllib import parse
import smtplib,uuid
from email.mime.text import MIMEText
from copy import deepcopy
import redis
import socket
import websocket
import ssl
import execjs

## exchange邮件发送相关的库包
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
urllib3.disable_warnings() # 可以避免老是报错...



class CookiesPool():
    """
        function:
            封装一个操作redis的对象, 把列表/哈希表/集合等redis数据结构的 '增删改查' 写成统一的'实例方法接口'
            pool的数据结构: 使用队列结构 (先进的先出, 适合爬虫项目)
                            所以: add是加到右边最后一个元素; get是左边第一个元素; pop也是左边第一个元素
        note:
            1. pool_type的种类:
                1. list
                2. dict
                3. set
    """
    def __init__(self, pool_name, pool_type="list", redis_host="localhost", redis_port=6379, db=0, decode_responses=True, **kwargs):
        if db:
            kwargs["db"] = db
        if decode_responses:
            kwargs["decode_responses"] = decode_responses
        self.redis = redis.StrictRedis(host="localhost", port=6379, **kwargs)
        self.pool_name = pool_name
        self.pool_type = pool_type
        # 先清空redis中的这个'键' (如果已经存在某些数据, 可能数据类型会和后面操作的方式对不上而报错)
        self.redis.delete(self.pool_name)


    def __str__(self):
        return str(self.values())


    def __repr__(self):
        "推荐用这个!"
        return str(self.values())


    def add(self, value, key="undefined"):
        "增"
        if self.pool_type == "list":
            res = self.redis.rpush(self.pool_name, value)
        elif self.pool_type == "dict":
            res = self.redis.hset(self.pool_name, key, value)
        return res


    def pop(self):
        "删"
        if self.pool_type == "list":
            res = self.redis.lpop(self.pool_name)
        elif self.pool_type == "dict":
            res = "'dict'类型的pool没有pop方法;\n"
        return res


    def delete(self, key):
        "删"
        if self.pool_type == "list":
            res = self.redis.lrem(self.pool_name, 1, key)
        elif self.pool_type == "dict":
            res = self.redis.hdel(self.pool_name, key)
        return res


    def get(self, key="undefined"):
        "查"
        if self.pool_type == "list":
            res = self.redis.lindex(self.pool_name, 0)
        elif self.pool_type == "dict":
            res = self.redis.hget(self.pool_name, key)
        return res


    def values(self):
        if self.pool_type == "list":
            res = self.redis.lrange(self.pool_name, 0, -1)
        elif self.pool_type == "dict":
            # "dict类型的, 直接返回items字典"
            res = self.redis.hgetall(self.pool_name)
        return res


    def length(self):
        if self.pool_type == "list":
            res = self.redis.llen(self.pool_name)
        elif self.pool_type == "dict":
            res = len(self.redis.hvals(self.pool_name))
        return res



class Utils_Crawl():
    def __init__(self):
        pass


    # 生产者
    def k_produce(self, lst=[], queue_name="unnamed", sub_queue_name="", produce_type="init"):
        """
        获取需要爬取的所有id,清空并存入redis的待爬队列中
        """
        # 0. 先获取redis的连接对象
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

        # 1. 先把传入的队列名称加上 ":" (方便后面redis中分级)
        if queue_name:
            queue_name += ":"
        if sub_queue_name:
            sub_queue_name += ":"


        # 2. 分流: 区分生产者类型
            ### 1. 清空原有e, 重新放入所有e
        if produce_type == "init":
            # 将lst中的所有 '元素' 放入待爬队列
            # 1. 先清空历史遗留的元素
            r.delete("{0}{1}pending_queue".format(queue_name, sub_queue_name))
            # 2. push所有元素
            if len(lst): # 如果lst没有元素,下面的lpush会报错
                r.lpush("{0}{1}pending_queue".format(queue_name, sub_queue_name), *lst)
            ### 2. 加入新的e
        elif produce_type == "add":
            if len(lst): # 如果lst没有元素,下面的lpush会报错
                r.lpush("{0}{1}pending_queue".format(queue_name, sub_queue_name), *lst)


    def k_consume_pool(self, consume_func, queue_name="unnamed", sub_queue_name="", thread_num=5, time_sleep=0.3):
        """
        function: 使用多线程，消费redis队列中的所有内容
                    (消费方式需用用consume_func函数来定义)
                    (可以是发起req，也可以是其他操作...)

        既然是多线程,一般需要用for循环,循环生成线程.
        再把这些子线程统一append到一个t_pool中管理.
        join()用于主线程阻塞等待这些子线程
        """
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

        #################################### 分割线 ##########################################
        def safety():
            """
            function: 确保不发生漏爬现象
            非常完整的req流程，可供多线程并发爬取，不会存在抢占资源的问题
            """

            # 如果待爬队列有元素,就一直循环爬取
            while r.llen("{0}{1}pending_queue".format(queue_name, sub_queue_name)):
                num = r.llen("{0}{1}pending_queue".format(queue_name, sub_queue_name))
                print("待爬队列中的剩余元素量:{}\n".format(num))
                # 1.从待爬队列获取出e
                e = r.rpop("{0}{1}pending_queue".format(queue_name, sub_queue_name))
                # 2.将 e 放入error_queue
                r.lpush("{0}{1}error_queue".format(queue_name, sub_queue_name), e)

                try:
                    # 3.真正执行任务的函数！！！（消费者函数）
                    consume_func(e)
                    # 4.将成功爬取的url存入已爬队列
                    r.sadd("{0}{1}crawled_queue".format(queue_name, sub_queue_name), e)
                    # 5.删掉错误队列中的响应元素
                    r.lrem("{0}{1}error_queue".format(queue_name, sub_queue_name), -1, e)

                # 发送req后,不管出现什么问题,都把url遗留在error_queue中
                except Exception as e:
                    print(e)
                    tb_txt = traceback.format_exc(limit=5)
                    print(tb_txt)
                    # 如果req访问出错,数据获取失败,不管什么原因,把这个错误id遗留在错误队列中
                    print("e={} 访问出错,遗留在错误队列中\n\n".format(e))
        #################################### 分割线 ##########################################

        # 1. 先把传入的队列名称加上 ":" (方便后面redis中分级)
        if queue_name:
            queue_name += ":"
        if sub_queue_name:
            sub_queue_name += ":"

        # 2.
        t_pool = []
        for _ in range(thread_num): # 此处创建5个线程来消费
            print("\n即将生成一个线程...")
            time.sleep(time_sleep)
            t = threading.Thread(target=safety)
            t.start()
            t_pool.append(t)
        for t in t_pool:
            t.join() # 主线程需要阻塞等待每一个子线程


    def k_error_to_pending(self, queue_name):
        """
        function : 把error队列的数据转移到待爬队列中,便于开始对error的req重新爬取
        """
        # 0. 获取redis的连接对象
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

        # 1. 翻转error队列
        error_lst = r.lrange("{0}:error_queue".format(queue_name), 0, -1)
        error_lst.reverse()

        # 2. 把error队列中的错误元素, 倾倒入待爬队列中
        if len(error_lst): # 如果lst没有元素,下面的lpush会报错
            r.lpush("{0}:pending_queue".format(queue_name), *error_lst)
        # 3. 删除error队列
        r.delete("{0}:error_queue".format(queue_name))


    def kill_error_queue(self, queue_name):
        "清空 error_queue 的元素"
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        r.delete("{queue_name}:error_queue".format(queue_name=queue_name))


    def k_crawl_error_again(self, queue_name, consume_func, thread_num=1, time_sleep=1, try_loops=1):
        "如果有错误req导致error_queue有留存元素,将其倒入pending_queue队列,重新对该部分爬取"
        r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
        for try_times in range(try_loops): # 重试2次
            # 如果error_queue队列中已经没有元素,则跳出循环
            error_lst = r.lrange("adjust_price:error_queue", 0, -1)
            if len(error_lst) == 0:
                break
            # 否则倾倒队列,重新生成多线程消费者消费
            k_error_to_pending(queue_name=queue_name)
            k_consume_pool(queue_name=queue_name, consume_func=consume_func, thread_num=thread_num, time_sleep=time_sleep)


    def get_js_txt_for_encrypt(self, js_full_path):
        """
        in: js代码的完整路径
            （经过自己过滤处理后，把所有可能用到的加密js函数全放在这个js文件中即可！！）
            必须要有个直接调用加密的函数
                eg.
                function encryptByDES(message, key) {.....}

        note:
            其实只要找到所有需要的js文件，直接复制、粘贴过来，都不需要修改什么，直接就可以用了诶！！！
            目前的难点是：1. 如何找到加密函数？   2. 如何把与加密相关的所有js文件都集齐、汇总到本js文件中
            难点1的思路：
                1. 使用事件断点：  click、xhr、encode解析、submit 等等
                2. 直接搜索关键词： encrypt, aes, submit, request, click, password, user, passpd, log, login
                3. 针对登录的form、输入密码的input等标签，后续js加密代码肯定需要使用这个标签获取这个input中的值，所以可以搜这个tag的id或类名
                4. 设置很多可能的断点，逐行逐行调试。配合使用堆栈的记录功能，快速跳转函数。(时刻关注local的变量值的变化)
            难点2的思路：
                1. 多配合"step into next function call" 的调试方式（可以下钻到更深一层的函数）
        """
        with open(js_full_path, "r", encoding="utf8") as file:
            js_txt = file.read()
        return js_txt


    def exec_js_function(self, js_full_path, func_name, *args):
        """
        function: 获取js代码的上下文，指定某个js函数，并传入相应个数的参数，得到js函数的返回值
        参数说明:
            1.解密js的完整路径
            2.所使用的函数
            3+.可以传入多个参数
        """
        # print(args)
        # print("---\n\n")
        # print(*args)
        js_txt = get_js_txt_for_encrypt(js_full_path)
        ctx = execjs.compile(js_txt, f"{FILE_PATH_FOR_HOME}/node_modules")
        result = ctx.call(func_name, *args)
        return result



utils_crawl = Utils_Crawl()


if __name__ == '__main__':
    # 测试一 : 价格系统
    js_full_path = "/Users/kerwin/MyBox/MyCode/Personal/django_test01/first_project/static/js/encryption_4_price_system.js"
    a = utils_crawl.exec_js_function(js_full_path, "encryptByDES", "ttt", "#z@i!r*o%o&m^")
    print(a)
    # 测试二 : 内网（库存系统）
    js_full_path = "/Users/kerwin/MyBox/MyCode/Personal/django_test01/first_project/static/js/encryption_4_ziroom_intranet.js"
    a = utils_crawl.exec_js_function(js_full_path, "encodeAes", "ttt")
    print(a)
    sys.exit()
