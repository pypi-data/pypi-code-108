# -*- coding: utf-8 -*-
# __author__ = "Casey"  395280963@qq.com
# Date: 2021-12-01  Python:3.6

import json
import random
import pymysql
import datetime
import traceback
from dbutils.pooled_db import PooledDB
import logging
import functools
from logging import handlers
from pyforest import LazyImport
os = LazyImport("import os")
re = LazyImport("import re")
time = LazyImport("import time")
json = LazyImport("import json")
httpx = LazyImport("import httpx")
ctypes = LazyImport("import ctypes")
random = LazyImport("import random")
pymysql = LazyImport("import pymysql")
ddddocr = LazyImport("import ddddocr")
difflib = LazyImport("import difflib")
hashlib = LazyImport("import hashlib")
datetime = LazyImport("import datetime")
requests = LazyImport("import requests")
traceback = LazyImport("import traceback")
Image = LazyImport("from PIL import Image")
BytesIO = LazyImport("from io import BytesIO")
logger = LazyImport("from loguru import logger")
ImageDraw = LazyImport("from PIL import ImageDraw")
ImageFont = LazyImport("from PIL import ImageFont")
TTFont = LazyImport("from fontTools.ttLib import TTFont")
PooledDB = LazyImport("from DBUtils.PooledDB import PooledDB")
RequestsConnectionError = LazyImport("from requests.exceptions import ConnectionError as RequestsConnectionError")


def cprint(*args, c=31):  # 红色=31 绿色=32 黄色=33 蓝色=34 洋红=35 青色=36
    if len(args) == 0:
        print(f"\033[{c}m\033[0m", flush=True)
    if len(args) == 1:
        print(f"\033[{c}m{args[0]}\033[0m", flush=True)
    else:
        p_str = ""
        for arg in args:
            p_str = f"{p_str}{arg} "
        print(f"\033[{c}m{p_str}\033[0m", flush=True)


class Auto_insert:
    def __init__(
        self,
        host="127.0.0.1",
        username="root",
        password="",
        port=3306,
        db="test",
        drop_column=None,
        pool_db=False,
        pool_num=10,
    ):
        if drop_column is None:
            drop_column = ["id"]
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.db = db
        self.pool_db = pool_db
        self.drop_column = drop_column  # 表删除字段
        self.pool_num = pool_num
        self.conn, self.cursor = self.sql_connect()
        self.table_name_list = self.get_db_name()
        self.column_list = self.get_columns()
        self.ping()

    def sql_connect(self):
        if self.pool_db:
            sql_pool = PooledDB(
                pymysql,
                self.pool_num,
                host=self.host,
                user=self.username,
                passwd=self.password,
                db=self.db,
                port=3306,
                charset="utf8",
                use_unicode=True,
            )
            conn = sql_pool.connection()
        else:
            conn = pymysql.connect(
                host=self.host,
                user=self.username,
                password=self.password,
                database=self.db,
                port=self.port,
                charset="utf8",
            )
        cursor = conn.cursor()
        return conn, cursor

    def get_db_name(self):
        sql = f"select table_name from information_schema.tables where table_schema='{self.db}'"
        self.cursor.execute(sql)
        db_list = self.cursor.fetchall()
        db_list = [data[0] for data in db_list]
        return db_list

    def get_columns(self):
        item = {}
        for table_name in self.table_name_list:
            sql = f"select column_name from information_schema.columns where table_name='{table_name}' and table_schema='{self.db}'"
            self.cursor.execute(sql)
            column_list = self.cursor.fetchall()
            column_list = [data[0] for data in column_list]
            insert_columns = [
                data for data in column_list if data not in self.drop_column
            ]
            item[table_name] = insert_columns
        return item

    def ping(self):
        error_count = 0
        while True:
            try:
                conn, cursor = self.sql_connect()
                return conn, cursor
            except Exception as e:
                fs = traceback.format_exc(chain=False)
                print(f"数据库连接失败,等待5s重试连接, error:{fs}")
                time.sleep(5)

                error_count += 1
                if error_count > 5:
                    print(f"数据库连接失败, 连接已断开! host:{self.host}, error:{fs}")
                    return None, None
                print(f"数据库连接失败, 正在尝试第 {error_count} 次重新连接... host:{self.host} ")

    def insert_data(self, item, table_name):
        """插入 mysql 数据
        :param item为字典，数据库字段与内容对应
        :param table_name:
        :return:
        """
        sql_conn, cursor = self.ping()
        if item and sql_conn and cursor:
            item_key = self.column_list.get(table_name)
            if item_key:
                item_values = [
                    f"'{item.get(key)}'"
                    if isinstance(item.get(key), str)
                    else f"{item.get(key)}".replace("None", "NULL")
                    for key in item_key
                ]
                insert = f"insert ignore into {table_name}({','.join(item_key)}) values({','.join(item_values)})"
                cursor.execute(insert)
                sql_conn.commit()
                print(
                    f"****************   table_name:{table_name} insert data success   ****************"
                )
            else:
                raise ValueError(f"不存在表:{table_name}")
        else:
            if not cursor or not sql_conn:
                with open("error_insert_data.txt", "a", encoding="utf8") as f:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                print("数据库连接异常，未插入数据字段保存在 error_insert_data.txt")
            else:
                print("item is None")
        cursor.close()
        sql_conn.close()

    def update_data(self, item, table_name):
        """更新 mysql数据
        :param  item示例 {
        xxx:xxx,
        xxx:xxx,
        update_id:{
            'key':xxx,
            'value':xxx
        }
        }:
        :param table_name: 表名
        :return:
        """
        sql_conn, cursor = self.ping()
        if item and sql_conn and cursor:
            item_key = self.column_list.get(table_name)
            if item_key:
                if item.get("update_id"):
                    update_id_data = item.pop("update_id")
                    update_item_key = [key for key in item.keys()]
                    update_item_values = [
                        f"'{item.get(key)}'"
                        if isinstance(item.get(key), str)
                        else f"{item.get(key)}".replace("None", "NULL")
                        for key in update_item_key
                    ]
                    update_content = ""
                    for i in range(len(update_item_key)):
                        update_content += (
                            f"{update_item_key[i]}"
                            + "="
                            + f"{update_item_values[i]}"
                            + ","
                        )
                    update = f"UPDATE {table_name} SET {update_content.rstrip(',')} WHERE {update_id_data.get('key')}={update_id_data.get('value')}"
                    cursor.execute(update)
                    sql_conn.commit()
                    print(
                        f"****************   table_name:{table_name} update data success   ****************"
                    )
                else:
                    raise ValueError("不存在更新的key: update_id")
            else:
                raise ValueError(f"不存在表:{table_name}")
        else:
            if not cursor or not sql_conn:
                with open("error_insert_data.txt", "a", encoding="utf8") as f:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
                print("数据库连接异常，未插入数据字段保存在 error_insert_data.txt")
            else:
                print("item is None")
        cursor.close()
        sql_conn.close()


class Logging(object):
    """
    Usage::

        # >>>
        # >>> logger = Logging()
        # >>> logger.info('Logging Example')
        # 2022-01-20 17:27:32.194 | INFO     | __main__:info:149 - Logging Example
        # >>>
    """

    t = time.strftime("%Y_%m_%d")
    # path = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), "logs")
    path = os.path.join('.', "logs")

    __instance = None
    logger.add(
        f"{path}/log_{t}_info.log",
        encoding="utf-8",
        enqueue=True,
        retention="1 months",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss}|{level}| {name}:{function}:{line}| {message}",
    )
    logger.add(
        f"{path}/log_{t}_error.log",
        encoding="utf-8",
        enqueue=True,
        retention="10 days",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss}|{level}| {name}:{function}:{line}| {message}",
    )
    logger.add(
        f"{path}/log_{t}_debug.log",
        encoding="utf-8",
        enqueue=True,
        retention="10 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss}|{level}| {name}:{function}:{line}| {message}",
    )

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Logging, cls).__new__(cls, *args, **kwargs)

        return cls.__instance

    @staticmethod
    def info(msg):
        return logger.info(msg)

    @staticmethod
    def debug(msg):
        return logger.debug(msg)

    @staticmethod
    def warning(msg):
        return logger.warning(msg)

    @staticmethod
    def error(msg):
        return logger.error(msg)


class SimpleHash(object):
    """
    BloomFilter Hash Function
    """

    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(len(value)):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class BloomFilter(object):
    """
    Usage::

      # >>> bf = BloomFilter(server, key, blockNum=1)  # you can increase blockNum if your are filtering too many urls
      # ... if is_contains(fp):
      # ...     print(f"{fp} 已存在")
      # ... else:
      # ...     bf.insert(fp)
      # >>>

    """

    def __init__(self, server, key, blockNum=1):
        """

        :param server: Redis Server
        :param key: Redis Key
        :param blockNum:
        """
        self.bit_size = 1 << 31  # Redis的String类型最大容量为512M，现使用256M
        self.seeds = [5, 7, 11, 13, 31]
        # self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.server = server
        self.key = key
        self.blockNum = blockNum
        self.hash_func = []
        for seed in self.seeds:
            self.hash_func.append(SimpleHash(self.bit_size, seed))

    def is_contains(self, str_input):
        """

        :param str_input: Filter Fingerprint
        :return:
        """
        if not str_input:
            return False
        ret = True

        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hash_func:
            loc = f.hash(str_input)
            ret = ret & self.server.getbit(name, loc)
        return ret

    def insert(self, str_input):
        name = self.key + str(int(str_input[0:2], 16) % self.blockNum)
        for f in self.hash_func:
            loc = f.hash(str_input)
            self.server.setbit(name, loc, 1)


def get_proxy(http2=False):
    """
    Get request Proxy
    :param http2:
    :return:
    """
    while True:
        try:
            response = requests.get(
                url="http://219.151.149.149:8888/get_ips/?user_code=688688&user_key=688688"
            ).json()
            proxy = random.choice(response["data"])
            if http2:
                return {"https://": "http://" + proxy, "http://": "http://" + proxy}
            return {"https": "http://" + proxy, "http": "http://" + proxy}
        except Exception as e:
            traceback.format_exc(e)


def random_ua(is_set=2):
    """
    Random UserAgent
    :param is_set: default -> win10 && Chrome
    :return:
    """
    s_ver = [
        str(random.randint(10, 99)),
        "0",
        str(random.randint(1000, 9999)),
        str(random.randint(100, 999)),
    ]
    version = ".".join(s_ver)
    webkit = "AppleWebKit/537.36 (KHTML, like Gecko)"
    mac = "_".join(
        [str(random.randint(8, 12)) for _ in range(2)] + [str(random.randint(1, 10))]
    )
    if is_set:
        typeid = random.randint(1, 6)
    else:
        typeid = 7
    if typeid == 1:
        ua_ua = "Mozilla/5.0 (Windows NT 7.1; WOW64) %s Chrome/%s Safari/537.36" % (
            webkit,
            version,
        )
    elif typeid == 2:
        ua_ua = "Mozilla/5.0 (Windows NT 10.1; WOW64) %s Chrome/%s Safari/537.36" % (
            webkit,
            version,
        )
    elif typeid == 3:
        ua_ua = "Mozilla/5.0 (Windows NT 8.1; WOW64) %s Chrome/%s Safari/537.36" % (
            webkit,
            version,
        )
    elif typeid == 4:
        ua_ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X %s) %s Chrome/%s Safari/537.36"
            % (mac, webkit, version)
        )
    elif typeid == 5:
        ua_ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X %s) %s Chrome/%s Safari/537.36"
            % (mac, webkit, version)
        )
    elif typeid == 6:
        ua_ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X %s) %s Chrome/%s Safari/537.36"
            % (mac, webkit, version)
        )
    else:
        ua_ua = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X %s) %s Chrome/%s Safari/537.36"
            % (mac, webkit, version)
        )
    return ua_ua


def base_requests(
    url,
    headers,
    method="get",
    data=None,
    params=None,
    json=None,
    retry: int = 5,
    session=None,
    proxies=None,
    verify=False,
    http2=False,
    timeout=(20, 30),
    **kwargs,
):
    """
    Send a Get or Post Request with Retry Mechanism and Http2.0
    :param url:
    :param headers:
    :param method:
    :param data:
    :param params:
    :param json:
    :param retry:
    :param session:
    :param proxies:
    :param verify:
    :param http2: default -> http1.1
    :param timeout:
    :param kwargs:
    :return:
    """
    for _ in range(retry):
        try:

            if http2:
                session = session or httpx.Client(
                    http2=http2, headers=headers, verify=verify, proxies=proxies
                )
                if method.lower() == "get":
                    response = session.get(
                        url=url, params=params, timeout=timeout, **kwargs
                    )
                else:
                    response = session.post(
                        url=url,
                        params=params,
                        json=json,
                        data=data,
                        timeout=timeout,
                        **kwargs,
                    )
            else:
                response = (session or requests.Session()).request(
                    method=method.lower(),
                    url=url,
                    headers=headers,
                    data=data,
                    params=params,
                    json=json,
                    verify=verify,
                    proxies=proxies,
                    timeout=timeout,
                    **kwargs,
                )

            if 200 <= response.status_code < 300:
                return response
            else:
                continue

        except RequestsConnectionError:
            proxies = get_proxy(http2)
            continue
        except Exception as err:
            logger.debug(err)
            proxies = get_proxy(http2)
            continue
    else:
        return None


def md5_encrypt(content):
    """
    :param content:
    :return:
    """
    if (
        isinstance(content, list)
        or isinstance(content, tuple)
        or isinstance(content, str)
    ):
        content = str(content)
    if isinstance(content, dict):
        content = json.dumps(content)
    m = hashlib.md5()
    if isinstance(content, str):
        content = content.encode("utf-8")
    m.update(content)
    return m.hexdigest()


def int_overflow(val: int):
    """
    Process JavaScript nums Overflow
    :param val:
    :return:
    """
    maxint = 2147483647
    if not -maxint - 1 <= val <= maxint:
        val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
    return val


def right_shift(n, i):
    """
    Python Operator ">>"
    :param n:
    :param i:
    :return:
    """
    if n < 0:
        n = ctypes.c_uint32(n).value
    if i < 0:
        return -int_overflow(n << abs(i))
    if i != 0:
        return int_overflow(n >> i)
    else:
        return n


def string_similar(s1: str, s2: str):
    """
    Compare Strings Similar Percentage
    :param s1:
    :param s2:
    :return: :float: percentage
    """
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


def format_time(time_str):
    """
    :param time_str:
    :return:
    """
    try:
        timestamp = int(int(time_str) / 1000)
        if timestamp >= 0:
            time_array = time.localtime(timestamp)
            other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        else:
            other_style_time = datetime.datetime(1970, 1, 2) + datetime.timedelta(
                seconds=timestamp
            )
        return str(other_style_time)
    except ValueError:
        reg = r"([0-9]{4}).*?([0-1]{0,1}[0-9]).*?([0-3]{0,1}[0-9])"
        time_str = re.search(reg, time_str)
        if time_str:
            year = time_str.group(1)
            month = time_str.group(2)
            day = time_str.group(3)
            time_str = year + "-" + month + "-" + day
            time_stamp = int(time.mktime(time.strptime(time_str, "%Y-%m-%d %H:%M:%S")))
            return time_stamp
    return
