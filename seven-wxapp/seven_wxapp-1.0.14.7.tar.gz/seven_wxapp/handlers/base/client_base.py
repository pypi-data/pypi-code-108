# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-01-05 17:16:17
@LastEditTime: 2022-01-24 14:12:42
@LastEditors: HuangJianYi
@Description: 
"""
import hashlib
import ast
import re
import random
import emoji
import json
from urllib.parse import parse_qs, urlparse
from emoji import unicode_codes
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_framework.redis import *
from seven_wxapp.handlers.base.seven_helper import *


class ClientBaseHandler(BaseApiHandler):
    """
    :description: 客户端基类
    """
    def prepare_ext(self):
        try:

            clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
            if clientheaderinfo_string:
                # 将设备信息字符串转为字典类型
                device_dict = self.get_device_info(clientheaderinfo_string)
                self.device_info = device_dict

        except Exception as ex:
            self.logging_link_error(str(ex) + "【获取头部参数出现异常】")

    device_info = {}  # 头部参数
    param_info = {}  # 请求参数

    def redis_init(self, db=None, config_dict=None, decode_responses=False):
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
        redis_cli = RedisHelper.redis_init(host, port, db, password, config_dict, decode_responses)
        return redis_cli

    def get_now_datetime(self, hour=0):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJianYi
        """
        return TimeHelper.add_hours_by_format_time(hour=hour)

    def check_post(self, redis_key, expire=1):
        """
        :description: 请求太频繁校验
        :param redis_key：key
        :param expire：过期时间(单位:秒)
        :return: bool
        :last_editors: HuangJianYi
        """
        post_value = self.redis_init().get(redis_key)
        if post_value == None:
            self.redis_init().set(redis_key, 10, ex=expire)
            return True
        return False

    def check_lpush(self, queue_name, value, limitNum=100):
        """
        :description: 入队列校验
        :return: bool
        :last_editors: HuangJianYi
        """
        list_len = self.redis_init().llen(queue_name)
        if int(list_len) >= int(limitNum):
            return False
        self.redis_init().lpush(queue_name, json.dumps(value))
        return True

    def lpop(self, queue_name):
        """
        :description: 出队列
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        result = self.redis_init().lpop(queue_name)
        return result

    def acquire_lock(self, lock_name, acquire_time=10, time_out=5):
        """
        :description: 获取一个分布式锁
        :param lock_name：锁定名称
        :param acquire_time: 客户端等待获取锁的时间
        :param time_out: 锁的超时时间
        :return bool
        :last_editors: HuangJianYi
        """
        identifier = str(uuid.uuid4())
        end = time.time() + acquire_time
        lock = "lock:" + lock_name
        while time.time() < end:
            if self.redis_init().setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                self.redis_init().expire(lock, time_out)
                return identifier
            if not self.redis_init().ttl(lock):
                self.redis_init().expire(lock, time_out)
            time.sleep(0.001)
        return False

    def release_lock(self, lock_name, identifier):
        """
        :description: 释放一个锁
        :param lock_name：锁定名称
        :param identifier: identifier
        :return bool
        :last_editors: HuangJianYi
        """
        lock = "lock:" + lock_name
        pip = self.redis_init().pipeline(True)
        while True:
            try:
                pip.watch(lock)
                lock_value = self.redis_init().get(lock)
                if not lock_value:
                    return True
                if lock_value.decode() == identifier:
                    pip.multi()
                    pip.delete(lock)
                    pip.execute()
                    return True
                pip.unwatch()
                break
            except redis.excetions.WacthcError:
                pass
        return False

    def random_weight(self, random_prize_dict_list):
        """
        :description:  根据权重算法获取商品
        :param random_prize_dict_list：权重列表
        :return: str
        :last_editors: HuangJianYi
        """
        total = sum(random_prize_dict_list.values())  # 权重求和
        ra = random.uniform(0, total)  # 在0与权重和之前获取一个随机数
        curr_sum = 0
        ret = None
        keys = random_prize_dict_list.keys()
        for k in keys:
            curr_sum += random_prize_dict_list[k]  # 在遍历中，累加当前权重值
            if ra <= curr_sum:  # 当随机数<=当前权重和时，返回权重key
                ret = k
                break
        return ret

    def get_device_info(self, device_string):
        """
        :description: 获取头部参数字典
        :param device_string:头部信息串
        :last_editors: HuangJianYi
        """
        device_dict = {}
        info_model = parse_qs(device_string)
        device_dict["p_id"] = int(info_model["PID"][0])
        device_dict["union_id"] = "" if "UnionID" not in info_model.keys() else info_model["UnionID"][0]
        device_dict["height"] = 0 if "Height" not in info_model.keys() else int(float(info_model["Height"][0]))
        device_dict["width"] = 0 if "Width" not in info_model.keys() else int(float(info_model["Width"][0]))
        device_dict["version"] = "" if "Version" not in info_model.keys() else info_model["Version"][0]  # 客户端版本号
        device_dict["app_version"] = "" if "AppVersion" not in info_model.keys() else info_model["AppVersion"][0]  # 小程序版本号
        device_dict["net"] = "" if "Net" not in info_model.keys() else info_model["Net"][0]
        device_dict["model_p"] = "" if "Model" not in info_model.keys() else info_model["Model"][0]
        device_dict["lang"] = "" if "Lang" not in info_model.keys() else info_model["Lang"][0]
        device_dict["ver_no"] = "" if "VerNo" not in info_model.keys() else info_model["VerNo"][0]  #接口版本号
        device_dict["chid"] = 0 if "CHID" not in info_model.keys() else int(info_model["CHID"][0])
        device_dict["signature_stamp"] = 0 if "SignatureStamp" not in info_model.keys() else int(info_model["SignatureStamp"][0])
        device_dict["signature_md5"] = "" if "SignatureMD5" not in info_model.keys() else info_model["SignatureMD5"][0]
        return device_dict

    def get_request_param(self, param_name, default="", filter_sql=True, strip=True):
        """
        :description: 二次封装获取参数
        :param param_name: 参数名
        :param default: 如果无此参数，则返回默认值
        :param filter_sql: 是否过滤sql关键字
        :return: 参数值
        :last_editors: HuangJianYi
        """
        param_ret = ""
        if self.request.method == "POST" and self.request.body:
            if not self.param_info:
                self.param_info = json.loads(self.request.body)
            param_ret = self.param_info[param_name] if self.param_info.__contains__(param_name) else ""
        else:
            param_ret = self.get_argument(param_name, default, strip=strip)
        if param_ret == "" or param_ret == "undefined":
            param_ret = default
        if param_name != "avatar" and isinstance(param_ret, str):
            param_ret = self.sql_filter(param_ret) if filter_sql else param_ret
        return param_ret

    def sql_filter(self, sql):
        """
        :description: 过滤特殊字符
        :param sql: 过滤字符串
        :return: 过滤结果
        :last_editors: HuangJianYi
        """
        char_list = ["and", "or", "exec", "execute", "insert", "select", "delete", "update", "alter", "create", "drop", "count", "from", "\*", "chr", "char", "asc", "mid", "substring", "master", "truncate", "declare", "xp_cmdshell", "restore", "backup", "net +user", "net +localgroup +administrators"]
        for char in char_list:
            sql = sql.replace(char.lower(), "")
            sql = sql.replace(char.upper(), "")
        return sql

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
            if "Expecting property name enclosed" in str(ex):
                return json.loads(self.json_dumps(rep_str))

    def json_dumps(self, rep_dic):
        """
        :description: 用于将字典形式的数据转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        if isinstance(rep_dic, str):
            rep_dic = ast.literal_eval(rep_dic)
        if hasattr(rep_dic, '__dict__'):
            rep_dic = rep_dic.__dict__
        # return json.dumps(rep_dic, ensure_ascii=False, cls=JsonEncoder)
        return json.dumps(obj=rep_dic, ensure_ascii=False, cls=JsonEncoder, default=lambda x: (x.__dict__ if not isinstance(x, datetime.datetime) else datetime.datetime.strftime(x, '%Y-%m-%d %H:%M:%S')) if not isinstance(x, decimal.Decimal) else float(x), sort_keys=False, indent=2)

    def client_reponse_json_success(self, data=None):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.client_reponse_common(data=data)

    def client_reponse_json_error(self, error_code="", error_message="", data=None, log_type=0):
        """
        :description: 通用错误返回json结构
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :param data: 返回结果对象，即为数组，字典
        :param log_type: 日志记录类型（0-不记录，1-info，2-error）
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if log_type == 1:
            self.logging_link_info(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        elif log_type == 2:
            self.logging_link_error(f"{error_code}\n{error_message}\n{data}\n{self.request}")
        self.client_reponse_common(False, data, error_code, error_message)

    def client_reponse_common(self, success=True, data=None, error_code="", error_message=""):
        """
        :description: 输出公共json模型,由配置文件的字段client_result_encrypt来据决定输出结果是否加密
        :param success: 布尔值，表示本次调用是否成功
        :param data: 类型不限，调用成功（success为true）时，服务端返回的数据
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJingCan
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        template_value = {}
        template_value['success'] = success
        template_value['data'] = data
        template_value['error_code'] = error_code
        template_value['error_message'] = error_message

        # rep_dic = {}
        # rep_dic['success'] = True
        # rep_dic['data'] = template_value
        client_result_encrypt = config.get_value("client_result_encrypt", True)
        if client_result_encrypt == True:
            self.http_reponse("0" + self.base64_encode(self.json_dumps(template_value)))
        else:
            self.http_reponse(self.json_dumps(template_value))

    def base64_encode(self, source, encoding="utf-8"):
        """
        :Description: base64加密
        :param source: 需加密的字符串
        :return: 加密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        import base64
        encode_string = str(base64.b64encode(source.encode(encoding=encoding)), 'utf-8')
        return encode_string

    def base64_decode(self, source):
        """
        :Description: base64解密
        :param source: 需加密的字符串
        :return: 解密后的字符串
        :last_editors: HuangJianYi
        """
        if not source.strip():
            return ""
        import base64
        decode_string = str(base64.b64decode(source), 'utf-8')
        return decode_string

    def emoji_base64_to_emoji(self, text_string):
        """
        :description: 把加密后的表情还原
        :param text_string: 加密后的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        results = re.findall('\[em_(.*?)\]', text_string)
        if results:
            for item in results:
                text_string = text_string.replace("[em_{0}]".format(item), self.base64_decode(item))
        return text_string

    def emoji_to_emoji_base64(self, text_string):
        """
        :description: emoji表情转为[em_xxx]形式存于数据库,打包每一个emoji
        :description: 性能遇到问题时重新设计转换程序
        :param text_string: 未加密的字符串
        :return: 解密后的表情字符串
        """
        list_e = [i for i in text_string]
        for location, item_emoji in enumerate(text_string):
            if item_emoji in unicode_codes.UNICODE_EMOJI:
                bytes_item_emoji = item_emoji.encode("utf-8")
                emoji_base64 = str(base64.b64encode(bytes_item_emoji), "utf-8")
                list_e[location] = "[em_" + emoji_base64 + "]"

        ret = "".join(list_e)
        return ret

    def get_signature_md5(self, request_param_dict, client_encrypt_key):
        """
        :description: 参数按照加密规则进行MD5加密 如果参数包含特殊字符最好进行base64加密,避免出现签名错误
        :description: 签名规则 SignatureMD5= ((参数1=参数1值&参数2=参数2值&SignatureStamp={SignatureStamp}))+密钥)进行Md5加密，参数顺序按照字母表的顺序排列
        :param request_param_dict: 请求参数字典
        :param client_encrypt_key: 接口密钥
        :return: 加密后的md5值，跟客户端传来的加密参数进行校验
        """
        request_sign_params = {}
        for k, v in request_param_dict.items():
            if k == "ParamSignatureMD5":
                continue
            if k == "SignatureMD5":
                continue
            request_sign_params[k] = str(v).replace(" ", "_seven_").replace("(", "_seven1_").replace(")", "_seven2_")
        request_params_sorted = sorted(request_sign_params.items(), key=lambda e: e[0], reverse=False)
        request_message = "&".join(k + "=" + CodingHelper.url_encode(v) for k, v in request_params_sorted)
        request_message = request_message.replace("_seven_", "%20").replace("_seven1_", "(").replace("_seven2_", ")").replace("%27", "'")
        # MD5摘要
        request_encrypt = hashlib.md5()
        request_encrypt.update((request_message + str(client_encrypt_key)).encode("utf-8"))
        check_request_signature_md5 = request_encrypt.hexdigest().lower()
        return check_request_signature_md5

    def get_real_ip(self):
        """
        :description: 获取真实IP
        :return:
        """
        ip = self.get_remote_ip()
        if ip and "," in ip:
            return ip.split(",")[0]
        else:
            return ip

    def check_common(self, act_dict, user_dict, task_dict, login_token, check_task=True):
        """
        :description: 做任务前的资格校验
        :param act_dict: 活动信息
        :param user_dict: 用户信息
        :param task_dict: 任务信息
        :param login_token: 访问令牌
        :param check_task: 任务校验
        :return:
        :last_editors: HuangJingCan
        """
        invoke_result = {}
        invoke_result['code'] = "0"
        invoke_result['message'] = "成功"
        task_type = 0
        if check_task:
            if not task_dict:
                invoke_result['code'] = "NoTask"
                invoke_result['message'] = "对不起，任务不存在"
                return invoke_result
            if task_dict['is_release'] == 0:
                invoke_result['code'] = "NoRelease"
                invoke_result['message'] = "对不起,未配置任务"
                return invoke_result
            if not task_dict['task_config']:
                invoke_result['code'] = "NoRelease"
                invoke_result['message'] = "对不起,未配置任务"
                return invoke_result
            task_type = task_dict['task_type']

        #请求太频繁限制
        if self.check_post(f"Task_Post_{str(act_dict['id'])}_{str(task_type)}_{str(user_dict['id'])}") == False:
            invoke_result['code'] = "HintMessage"
            invoke_result['message'] = "对不起，请稍后再试"
            return invoke_result

        if not act_dict:
            invoke_result['code'] = "NoAct"
            invoke_result['message'] = "对不起，活动不存在"
            return invoke_result

        if not user_dict:
            invoke_result['code'] = "NoUser"
            invoke_result['message'] = "对不起，用户不存在"
            return invoke_result
        if user_dict['user_state'] == 1:
            invoke_result['code'] = "UserState"
            invoke_result['message'] = "对不起，账号异常，请联系客服处理"
            return invoke_result
        if login_token not in ('', user_dict['login_token']):
            invoke_result['code'] = "ErrorToken"
            invoke_result['message'] = "对不起，已在另一台设备登录,无法操作"
            return invoke_result

        return invoke_result


def client_filter_check_params(must_params=None):
    """
    :description: 参数过滤装饰器 仅限handler使用,
                  提供参数的检查及获取参数功能
                  装饰器使用方法:
                  @client_filter_check_params("param_a,param_b,param_c")  或
                  @client_filter_check_params(["param_a","param_b,param_c"])
                  参数获取方法:
                  self.request_params[param_key]
    :param must_params: 必须传递的参数集合
    :last_editors: HuangJianYi
    """
    def check_params(handler):
        def wrapper(self, **args):
            self.request_params = {}
            if type(must_params) == str:
                must_array = must_params.split(",")
            if type(must_params) == list:
                must_array = must_params
            if "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                json_params = {}
                try:
                    json_params = json.loads(self.request.body)
                except:
                    self.client_reponse_json_error("ParamError", "参数错误,缺少必传参数")
                    return
                if json_params:
                    for field in json_params:
                        self.request_params[field] = json_params[field]
            else:
                for field in self.request.arguments:
                    self.request_params[field] = self.get_param(field)
            if must_params:
                for must_param in must_array:
                    if not must_param in self.request_params or self.request_params[must_param] == "":
                        self.client_reponse_json_error("ParamError", "参数错误,缺少必传参数")
                        return
            return handler(self, **args)

        return wrapper

    return check_params


def client_filter_check_head(is_check=True, no_check_params=None):
    """
    :description: 头部过滤装饰器 仅限handler使用
    :param is_check: 是否开启校验
    :param no_check_params: 不加入参数校验的参数集合
    :last_editors: HuangJianYi
    """
    def check_head(handler):
        def wrapper(self, **args):
            is_check_head = config.get_value("is_check_head", True)
            if is_check_head == False:
                is_check = False
            else:
                is_check = True
            if is_check == True:
                try:
                    if type(no_check_params) == str:
                        no_check_array = no_check_params.split(",")
                    elif type(no_check_params) == list:
                        no_check_array = no_check_params
                    else:
                        no_check_array = []
                    client_encrypt_key = config.get_value("client_encrypt_key", "3924e337a476475e95b2b341eaba8c1c")
                    # 验证是否有设备信息
                    clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
                    # clientheaderinfo_string = "CHID=1&Height=520&Lang=zh_CN&Model=iPhone%205&Net=unknown&PID=1&PixelRatio=2&SignatureStamp=1611321295380&Ver=1&Version=7.0.4&Width=320"
                    if clientheaderinfo_string:
                        # 将设备信息字符串转为字典类型
                        device_dict = self.get_device_info(clientheaderinfo_string)
                        # 验证签名超时 10分钟过期
                        now_time = TimeHelper.get_now_timestamp(True)
                        if now_time - device_dict["signature_stamp"] > int(1000 * 60 * 10):
                            return self.client_reponse_json_error("SignatureStamp", "登录超时,请重新进入小程序")
                        # 验证是否有头部信息签名
                        if not device_dict.__contains__("signature_md5"):
                            return self.client_reponse_json_error("NoSignatureMD5", "缺少参数SignatureMD5")
                        # 验证头部签名是否成功
                        client_head_dict = dict([(k, v[0]) for k, v in parse_qs(clientheaderinfo_string, True).items() if k != "SignatureMD5" and not k in no_check_array])
                        head_signature_md5 = self.get_signature_md5(client_head_dict, client_encrypt_key)
                        signature_md5 = device_dict["signature_md5"].lower()
                        if signature_md5 != head_signature_md5:
                            return self.client_reponse_json_error("SignatureFail", "头部签名验证失败")
                        # 验证参数
                        request_param_dict = {}
                        if self.request.method != "GET" and self.request.body:
                            request_param_dict = json.loads(self.request.body)
                        else:
                            request_param_dict = dict([(k, v[0]) for k, v in parse_qs(self.request.query, True).items()])
                        if not request_param_dict.__contains__("ParamSignatureMD5"):
                            return self.client_reponse_json_error("SignatureFail", "缺少参数ParamSignatureMD5")
                        check_request_signature_md5 = self.get_signature_md5(request_param_dict, client_encrypt_key)
                        param_signature_md5 = request_param_dict["ParamSignatureMD5"].lower()
                        if check_request_signature_md5 != param_signature_md5:
                            return self.client_reponse_json_error("ParamSignatureFail", "参数签名验证失败")
                    else:
                        return self.client_reponse_json_error("NoDeviceInfo", "没有提交设备信息")
                except Exception as ex:
                    self.logging_link_error(str(ex) + "【头部校验】")
                    return self.client_reponse_json_error("Error", "服务端错误")

            return handler(self, **args)

        return wrapper

    return check_head