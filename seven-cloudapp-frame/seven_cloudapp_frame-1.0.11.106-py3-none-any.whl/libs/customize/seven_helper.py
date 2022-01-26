# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2021-07-15 11:54:54
@LastEditTime: 2022-01-22 11:44:56
@LastEditors: HuangJianYi
:description: 常用帮助类
"""
from seven_framework import *
from seven_framework.redis import *
from emoji import unicode_codes
import random
import datetime
import re
import ast



class SevenHelper:
    """
    :description: 常用帮助类 提供常用方法 如：字典列表合并、请求太频繁校验、（入队列、出队列、校验队列长度 主要用于流量削峰场景）、创建分布式锁、释放分布式锁、序列化、反序列化、生成订单号等
    """
    @classmethod
    def redis_init(self, db=None, config_dict=None, decode_responses=True):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJianYi
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, config_dict=config_dict, decode_responses=decode_responses)
        return redis_cli

    @classmethod
    def is_continue_request(self, cache_key, expire=500):
        """
        :description: 请求太频繁校验
        :param cache_key：自定义cache_key
        :param expire：过期时间，单位毫秒
        :return: bool true-代表连续请求进行限制，false-代表跳过限制
        :last_editors: HuangJianYi
        """
        if config.get_value("is_pressure_test",False): #是否进行压力测试
            return False
        redis_init = self.redis_init()
        post_value = redis_init.get(cache_key)
        if post_value == None:
            redis_init.set(cache_key, 10, px=expire)
            return False
        return True

    @classmethod
    def redis_check_llen(self,queue_name,queue_lenth=100):
        """
         :description: 校验队列长度
         :param queue_name：自定义队列名称
         :param queue_lenth：队列长度
         :return: bool False-代表达到长度限制，进行拦截
         :last_editors: HuangJianYi
         """
        redis_init = self.redis_init()
        list_len = redis_init.llen(queue_name)
        if int(list_len) >= int(queue_lenth):
            return True
        else:
            return False

    @classmethod
    def redis_lpush(self, queue_name, value, expire):
        """
         :description: 入队列
         :param queue_name：自定义队列名称
         :param value：加入队列的数据
         :param expire：过期时间，单位秒
         :return:
         :last_editors: HuangJianYi
         """
        redis_init = self.redis_init()
        redis_init.lpush(queue_name, json.dumps(value))
        redis_init.expire(queue_name,expire)

    @classmethod
    def redis_lpop(self, queue_name):
        """
         :description: 出队列
         :param queue_name：队列名称
         :return: 
         :last_editors: HuangJianYi
         """
        result = self.redis_init().lpop(queue_name)
        return result

    @classmethod
    def redis_acquire_lock(self, lock_name, acquire_time=3, time_out=4):
        """
        :description: 创建分布式锁
        :param lock_name：锁定名称
        :param acquire_time: 客户端等待获取锁的时间,单位秒
        :param time_out: 锁的超时时间,单位秒
        :return 分布式锁是否获得（True获得False未获得）和解锁钥匙（释放锁时需传入才能解锁成功）
        :last_editors: HuangJianYi
        """
        identifier = str(uuid.uuid4())
        end = time.time() + acquire_time
        lock = "lock:" + lock_name
        redis_init = self.redis_init()
        while time.time() < end:
            if redis_init.setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                redis_init.expire(lock, time_out)
                return True,identifier
            if redis_init.ttl(lock) == -1 or redis_init.ttl(lock) == None:
                redis_init.expire(lock, time_out)
            time.sleep(0.001)
        return False,""

    @classmethod
    def redis_release_lock(self, lock_name, identifier):
        """
        :description: 释放分布式锁
        :param lock_name：锁定名称
        :param identifier: identifier
        :return bool
        :last_editors: HuangJianYi
        """
        lock = "lock:" + lock_name
        redis_init = self.redis_init()
        pip = redis_init.pipeline(True)
        try:
            pip.watch(lock)
            lock_value = redis_init.get(lock)
            if not lock_value:
                return True
            if lock_value == identifier:
                pip.multi()
                pip.delete(lock)
                pip.execute()
                return True
            pip.unwatch()
            return False
        except Exception:
            pip.unwatch()
            return False

    @classmethod
    def merge_dict_list(self, source_dict_list, source_key, merge_dict_list, merge_key, merge_columns_names='', exclude_merge_columns_names=''):
        """
        :description: 两个字典列表合并
        :param source_dict_list：源字典表
        :param source_key：源表用来关联的字段
        :param merge_dict_list：需要合并的字典表
        :param merge_key：需要合并的字典表用来关联的字段
        :param merge_columns_names：需要合并的字典表中需要展示的字段
        :param exclude_merge_columns_names：需要合并的字典表中不需要展示的字段
        :return: 
        :last_editors: HuangJianYi
        """
        result = []
        if merge_columns_names:
            list_key = list(merge_columns_names.split(","))
        else:
            list_key = list(merge_dict_list[0].keys()) if len(merge_dict_list)>0 else []
        if exclude_merge_columns_names:
            exclude_key = list(exclude_merge_columns_names.split(","))
            list_key = list(set(list_key).difference(set(exclude_key)))
        for source_dict in source_dict_list:
            info_list = [i for i in merge_dict_list if source_dict[source_key] and str(i[merge_key]) == str(source_dict[source_key])]
            if info_list:
                source_dict = dict(source_dict, **dict.fromkeys(list_key))
                for item in list_key:
                    source_dict[item] = info_list[0].get(item)
            else:
                result_key = []
                for item in list_key:
                    if item not in source_dict.keys():
                        result_key.append(item)
                source_dict = dict(source_dict, **dict.fromkeys(result_key))
            result.append(source_dict)
        return result

    @classmethod
    def auto_mapper(self, s_model, map_dict=None):
        '''
        :description: 对象映射（把map_dict值赋值到实体s_model中）
        :param s_model：需要映射的实体对象
        :param map_dict：被映射的实体字典
        :return: obj
        :last_editors: HuangJianYi
        '''
        if map_dict:
            field_list = s_model.get_field_list()
            for filed in field_list:
                if filed in map_dict:
                    setattr(s_model, filed, map_dict[filed])
        return s_model

    @classmethod
    def get_condition_by_str_list(self, field_name, str_list):
        """
        :description: 根据str_list返回查询条件 in查询参数化，如：act_info_model.get_list("FIND_IN_SET(act_name,%s)", params=['活动1,活动2'])
        :param field_name: 字段名
        :param str_list: 字符串数组
        :return: 
        :last_editors: HuangJianYi
        """
        if not str_list:
            return ""
        list_str = ','.join(["'%s'" % str(item) for item in str_list])
        return f"{field_name} IN({list_str})"

    @classmethod
    def get_condition_by_int_list(self, field_name, int_list=None):
        '''
        :description: 根据int_list返回查询条件 in查询参数化，如：act_info_model.get_list("FIND_IN_SET(act_name,%s)", params=['活动1,活动2'])
        :param field_name:字段名
        :param int_list:整形数组
        :return: str
        :last_editors: HuangJianYi
        '''
        if not int_list:
            return ""
        list_str = str(int_list).strip('[').strip(']')
        return f"{field_name} IN({list_str})"

    @classmethod
    def get_condition_in(self, field_name, field_str, field_type=1):
        '''
        :description: 根据逗号分隔字符串合成条件
        :param field_name:字段名
        :param field_str:逗号分隔字符串
        :param field_type:字段类型（1整形2字符串）
        :return: 查询字符串
        :last_editors: HuangJianYi
        '''
        if not field_str:
            return ""
        str_list = []
        if field_type == 1:
            try:
                str_list = [int(x) for x in field_str.split(",")]
            except Exception as ex:
                pass
            if len(str_list) <= 0:
                return ""
            list_str = str(str_list).strip('[').strip(']')
        else:
            str_list = field_str.split(",")
            list_str = ','.join(["'%s'" % str(item) for item in str_list])
        return f"{field_name} IN({list_str})"

    @classmethod
    def is_ip(self, ip_str):
        """
        :description: 判断是否IP地址
        :param ip_str: ip串
        :return:
        :last_editors: HuangJianYi
        """
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(str(ip_str)):
            return True
        return False

    @classmethod
    def get_first_ip(self,remote_ip):
        """
        :description: 获取第一个IP
        :param remote_ip: ip串
        :return:
        """
        if remote_ip and "," in remote_ip:
            return remote_ip.split(",")[0]
        else:
            return remote_ip

    @classmethod
    def to_file_size(self, size):
        """
        :description: 文件大小格式化
        :param size：文件大小
        :return: str
        :last_editors: HuangJianYi
        """
        if size < 1000:
            return '%i' % size + 'size'
        elif 1024 <= size < 1048576:
            return '%.2f' % float(size / 1024) + 'KB'
        elif 1048576 <= size < 1073741824:
            return '%.2f' % float(size / 1048576) + 'MB'
        elif 1073741824 <= size < 1000000000000:
            return '%.2f' % float(size / 1073741824) + 'GB'
        elif 1000000000000 <= size:
            return '%.2f' % float(size / 1000000000000) + 'TB'

    @classmethod
    def get_random(self,length):
        """
        :description: 获取随机字符串
        :param length：长度
        :return: str
        :last_editors: HuangJianYi
        """
        result = ""
        for i in range(length):
            # n=1 生成数字  n=2 生成字母
            n = random.randint(1, 2)
            if n == 1:
                numb = random.randint(0, 9)
                result += str(numb)
            else:
                nn = random.randint(1, 2)
                cc = random.randint(1, 26)
                if nn == 1:
                    numb = chr(64 + cc)
                    result += numb
                else:
                    numb = chr(96 + cc)
                    result += numb
        return result

    @classmethod
    def get_random_switch_string(self, random_str, split_chars=","):
        """
        :description: 随机取得字符串
        :param trimChars：根据什么符号进行分割
        :return: str
        :last_editors: HuangJianYi
        """
        if random_str == "":
            return ""
        random_list = [i for i in random_str.split(split_chars) if i != ""]
        return random.choice(random_list)

    @classmethod
    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJianYi
        """
        add_hours = config.get_value("add_hours", 0)
        return TimeHelper.add_hours_by_format_time(hour=add_hours)

    @classmethod
    def get_now_int(self, hours=0, minutes=0, fmt='%Y%m%d%H%M%S'):
        """
        :description: 获取整形的时间 格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010
        :param hours: 需要增加的小时数
        :param hours: 需要增加的分钟数
        :param fmt: 时间格式
        :return:
        :last_editors: HuangJianYi
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(minutes=minutes, hours=hours))
        return int(now_date.strftime(fmt))

    @classmethod
    def get_now_hour_int(self, hours=0):
        """
        :description: 获取整形的小时2020050612
        :param hours: 需要增加的小时数
        :return: int（2020050612）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(hours=hours, fmt='%Y%m%d%H')

    @classmethod
    def get_now_day_int(self, hours=0):
        """
        :description: 获取整形的天20200506
        :param hours: 需要增加的小时数
        :return: int（20200506）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(hours=hours, fmt='%Y%m%d')

    @classmethod
    def get_now_month_int(self, hours=0):
        """
        :description: 获取整形的月202005
        :param hours: 需要增加的小时数
        :return: int（202005）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(hours=hours,fmt='%Y%m')

    @classmethod
    def get_date_list(self, start_date, end_date):
        """
        :description: 两个日期之间的日期列表
        :param start_date：开始日期
        :param end_date：结束日期
        :return: list
        :last_editors: HuangJianYi
        """
        if not start_date or not end_date:
            return []
        if ":" not in start_date:
            start_date+=" 00:00:00"
        if ":" not in end_date:
            end_date += " 00:00:00"
        datestart = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        dateend = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        date_list = []

        while datestart < dateend:
            date_list.append(datestart.strftime('%Y-%m-%d'))
            datestart += datetime.timedelta(days=1)
        return date_list

    @classmethod
    def get_page_count(self, page_size, record_count):
        """
        @description: 计算页数
        @param page_size：页大小
        @param record_count：总记录数
        @return: 页数
        @last_editors: HuangJianYi
        """
        page_count = record_count / page_size + 1
        if page_size == 0:
            page_count = 0
        if record_count % page_size == 0:
            page_count = record_count / page_size
        page_count = int(page_count)
        return page_count

    @classmethod
    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        ran_num = ""
        if ran == 1:
            ran_num = random.randint(0, 9)
        elif ran == 2:
            ran_num = random.randint(10, 99)
        elif ran == 3:
            ran_num = random.randint(100, 999)
        elif ran == 4:
            ran_num = random.randint(1000, 9999)
        elif ran == 5:
            ran_num = random.randint(10000, 99999)
        # cur_time = TimeHelper.get_now_format_time('%Y%m%d%H%M%S%f')
        cur_time = TimeHelper.get_now_timestamp(True)
        order_id = str(cur_time) + str(ran_num)
        return order_id

    @classmethod
    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        try:
            rep_dic = ast.literal_eval(rep_dic)
        except ValueError:
            pass
        if hasattr(rep_dic, '__dict__'):
            rep_dic = rep_dic.__dict__
        return json.dumps(rep_dic, ensure_ascii=False, cls=JsonEncoder, default=lambda x: (x.__dict__ if not isinstance(x, datetime.datetime) else datetime.datetime.strftime(x, '%Y-%m-%d %H:%M:%S')) if not isinstance(x, decimal.Decimal) else float(x), sort_keys=False, indent=1)

    @classmethod
    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJianYi
        """
        try:
            return json.loads(rep_str)
        except Exception as ex:
            return json.loads(self.json_dumps(rep_str))

    @classmethod
    def get_sub_table(self,object_id,sub_count=0):
        """
        :description: 获取分表名称
        :param object_id:对象标识
        :param sub_count:分表数量
        :return:
        :last_editors: HuangJianYi
        """
        sub_table = None
        if not sub_count:
            return sub_table
        sub_table = str(object_id % sub_count)
        return sub_table

    @classmethod
    def remove_exponent(self, param):
        """
        :description: 去除参数多余的0，比如：100.00返回100，100.10返回100.1去掉尾数0
        :param param:要去除0的参数
        :return:
        :last_editors: HuangJianYi
        """
        if isinstance(param, str):
            param = decimal.Decimal(param)
        return param.to_integral() if param == param.to_integral() else param.normalize()