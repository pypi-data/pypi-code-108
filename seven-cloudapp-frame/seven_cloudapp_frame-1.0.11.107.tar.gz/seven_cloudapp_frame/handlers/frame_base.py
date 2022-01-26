# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-15 11:30:45
@LastEditTime: 2022-01-26 17:12:59
@LastEditors: HuangJianYi
@Description: 公共handler模块
"""

import ast
import random
import decimal
import hashlib
from copy import deepcopy
from asq.initiators import query
from urllib.parse import parse_qs, urlparse

from seven_framework.redis import *
from seven_framework.web_tornado.base_handler.base_api_handler import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.libs.customize.cryptography_helper import *
from seven_cloudapp_frame.libs.customize.string_helper import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.user_base_model import *
from seven_cloudapp_frame.models.db_models.app.app_info_model import *
from seven_cloudapp_frame.models.db_models.act.act_info_model import *
from seven_cloudapp_frame.models.db_models.operation.operation_log_model import *


class FrameBaseHandler(BaseApiHandler):
    """
    :description: 公共handler基类
    """
    def get_http_log_extra_dict(self):
        """
        :Description: 获取http日志参数字典
        :last_editors: HuangJianYi
        """
        dict_param = {}
        dict_param["open_id"] = self.get_open_id()
        if not dict_param["open_id"]:
            dict_param["open_id"] = self.get_user_id()
        dict_param["nick_name"] = self.get_user_nick()
        dict_param["app_id"] = self.get_app_id()
        if not dict_param["app_id"]:
            dict_param["app_id"] = self.get_source_app_id()
        return dict_param

    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        try:
            if self.__class__.__name__ == "IndexHandler":
                return
            self.is_encrypt = False
            #获取请求参数
            self._convert_request_params()
            # 标记日志请求关联
            dict_param = self.get_http_log_extra_dict()
            self._build_http_log(dict_param)
        except Exception as ex:
            if not hasattr(self, "request_code"):
                self.request_code = UUIDHelper.get_uuid()
            self.logging_link_error("【公共handler基类】" + traceback.format_exc())

    def options_async(self):
        self.response_json_success()

    def check_xsrf_cookie(self):
        return

    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_dumps(rep_dic)

    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJianYi
        """
        return SevenHelper.json_loads(rep_str)

    def get_param(self, param_name, default="", strip=True, filter_sql=False, filter_special_key=False):
        """
        :description: 二次封装获取参数
        :param param_name: 参数名
        :param default: 如果无此参数，则返回默认值
        :param filter_sql: 是否过滤sql关键字
        :param filter_special_key: 是否过滤sql特殊字符
        :return: 参数值
        :last_editors: HuangJianYi
        """
        param_ret = ""

        if self.request_params:
            param_ret = self.request_params[param_name] if self.request_params.__contains__(param_name) else ""
        else:
            param_ret = self.get_argument(param_name, default, strip=strip)
        if param_ret == "" or param_ret == "undefined":
            param_ret = default
        if filter_sql == True:
            param_ret = StringHelper.filter_sql(param_ret)
        if filter_special_key == True:
            param_ret = StringHelper.filter_special_key(param_ret)
        return param_ret

    def get_param_int(self, param_name, default=0, strip=True, filter_sql=False, filter_special_key=False):
        """
        :description: 二次封装获取参数转整形
        :param param_name: 参数名
        :param default: 如果无此参数，则返回默认值
        :param filter_sql: 是否过滤sql关键字
        :param filter_special_key: 是否过滤sql特殊字符
        :return: 转换后的参数值
        :last_editors: HuangJianYi
        """
        param =  self.get_param(param_name, default, strip, filter_sql, filter_special_key)
        try:
            param = int(param)
        except Exception as ex:
            param = default
        return param

    def _convert_request_params(self):
        """
        :Description: 转换请求参数 post请求：Content-type必须为application/json，前端必须对对象进行序列化转成json字符串，不能直接传对象,否则无法接收参数,存在特殊字符的参数必须进行url编码，否则+会被变成空值
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        self.request_params = {}
        client_encrypt_type = config.get_value("client_encrypt_type", 0)  #客户端加密类型 0-无，1-aes加密，2-md5加密
        server_encrypt_type = config.get_value("server_encrypt_type", 0)  #千牛端或后台加密类型 0-无，1-aes加密，2-md5加密
        is_encrypt = False if hasattr(self, "is_encrypt") and self.is_encrypt == False else True
        if is_encrypt == True and ("/server/" in self.request.uri and server_encrypt_type == 1) or ("/client/" in self.request.uri and client_encrypt_type == 1):
            encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
            #当有参数app_id时，优先取app_id，然后在是source_app_id
            if self.get_argument("app_id", "", strip=True):
                app_id = self.get_argument("app_id", "", strip=True)
            else:
                app_id = self.get_argument("source_app_id", "", strip=True)
            if not app_id:
                app_id = config.get_value("app_id")
            password = str(encrypt_key).replace("1", "l")
            if self.request.method == "POST" and "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                try:
                    json_params = json.loads(self.request.body)
                    if json_params:
                        for field in json_params:
                            self.request_params[field] = json_params[field]
                        par = json_params["par"] if json_params.__contains__("par") else ""
                        dv = json_params["dv"] if json_params.__contains__("dv") else ""
                        iv = app_id[0:10] + str(json_params["dv"])[0:6] if len(str(json_params["dv"])) >= 6 else ""
                        body_params = json.loads(CryptographyHelper.aes_decrypt(str(json_params["par"]), password, iv))
                        for field in body_params:
                            self.request_params[field] = body_params[field]
                except:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "参数解析错误"
                    return invoke_result_data
            else:
                for field in self.request.arguments:
                    self.request_params[field] = self.get_argument(field, "", strip=True)
                if "par" in self.request.arguments and "dv" in self.request.arguments:
                    par = self.get_argument("par", "", strip=True)
                    dv = self.get_argument("dv", "", strip=True)
                    iv = app_id[0:10] + str(dv)[0:6] if len(str(dv)) >= 6 else ""
                    try:
                        body_params = json.loads(CryptographyHelper.aes_decrypt(par, password, iv))
                        for field in body_params:
                            self.request_params[field] = body_params[field]
                    except:
                        invoke_result_data.success = False
                        invoke_result_data.error_code = "error"
                        invoke_result_data.error_message = "参数解析错误"
                        return invoke_result_data
        else:
            if self.request.method == "POST" and "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                try:
                    json_params = json.loads(self.request.body)
                    if json_params:
                        for field in json_params:
                            self.request_params[field] = json_params[field]
                except:
                    pass
            else:
                for field in self.request.arguments:
                    self.request_params[field] = self.get_argument(field, "", strip=True)

        return invoke_result_data

    def response_custom(self, rep_dic):
        """
        :description: 输出公共json模型
        :param rep_dic: 字典类型数据
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.http_response(self.json_dumps(rep_dic))

    def response_common(self, success=True, data=None, error_code="", error_message=""):
        """
        :description: 输出公共json模型
        :param success: 布尔值，表示本次调用是否成功
        :param data: 类型不限，调用成功（success为true）时，服务端返回的数据
        :param errorCode: 字符串，调用失败（success为false）时，服务端返回的错误码
        :param errorMessage: 字符串，调用失败（success为false）时，服务端返回的错误信息
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        if hasattr(data, '__dict__'):
            data = data.__dict__
        template_value = {}
        template_value['success'] = success
        is_encrypt = False if hasattr(self, "is_encrypt") and self.is_encrypt == False else True
        if is_encrypt == False:
            template_value['data'] = data
        else:
            client_encrypt_type = config.get_value("client_encrypt_type", 0)
            server_encrypt_type = config.get_value("server_encrypt_type", 0)
            if ("/server/" in self.request.uri and server_encrypt_type == 1) or ("/client/" in self.request.uri and client_encrypt_type == 1):
                dv = SevenHelper.get_random(16)
                encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
                if self.get_argument("app_id", "", strip=True):
                    app_id = self.get_argument("app_id", "", strip=True)
                else:
                    app_id = self.get_argument("source_app_id", "", strip=True)
                if not app_id:
                    app_id = config.get_value("app_id")
                password = str(encrypt_key).replace("1", "l")
                iv = app_id[0:10] + str(dv)[0:6] if len(str(dv)) >= 6 else ""
                template_value['data'] = CryptographyHelper.aes_encrypt(self.json_dumps(data), password, iv)
                template_value['dv'] = dv
            else:
                template_value['data'] = data
        template_value['error_code'] = "error" if not error_code and success == False else error_code
        template_value['error_message'] = "系统异常" if not error_message and success == False else error_message

        rep_dic = {}
        rep_dic['success'] = True
        rep_dic['data'] = template_value

        log_extra_dict = {}
        log_extra_dict["is_success"] = 1
        if success == False:
            log_extra_dict["is_success"] = 0

        self.http_reponse(self.json_dumps(rep_dic), log_extra_dict)

    def response_json_success(self, data=None):
        """
        :description: 通用成功返回json结构
        :param data: 返回结果对象，即为数组，字典
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.response_common(data=data)

    def response_json_error(self, error_code="", error_message="", data=None, log_type=0):
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
        self.response_common(False, data, error_code, error_message)

    def response_json_error_params(self):
        """
        :description: 通用参数错误返回json结构
        :param desc: 返错误描述
        :return: 将dumps后的数据字符串返回给客户端
        :last_editors: HuangJianYi
        """
        self.response_common(False, None, "params error", "参数错误")

    def return_dict_error(self, error_code="", error_message=""):
        """
        :description: 返回error信息字典模型
        :param errorCode: 字符串，服务端返回的错误码
        :param errorMessage: 字符串，服务端返回的错误信息
        :return: dict
        :last_editors: HuangJianYi
        """
        rep_dic = {}
        rep_dic['error_code'] = error_code
        rep_dic['error_message'] = error_message

        self.logging_link_error(f"{error_code}\n{error_message}\n{self.request}")

        return rep_dic

    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJianYi
        """
        return SevenHelper.get_now_datetime()

    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        return SevenHelper.create_order_id(ran)

    def check_continue_request(self, handler_name, app_id, object_id, expire=100):
        """
        :description: 一个用户同一handler频繁请求校验，只对同用户同接口同请求参数进行限制
        :param handler_name: handler名称
        :param app_id: 应用标识
        :param object_id: object_id(user_id或open_id)
        :param expire: 间隔时间，单位毫秒
        :return:满足频繁请求条件直接输出拦截
        :last_editors: HuangJianYi
        """
        result = False, ""
        if object_id and handler_name and app_id:
            sign = self.get_signature_md5(self.request_params)
            if SevenHelper.is_continue_request(f"continue_request:{handler_name}_{app_id}_{object_id}_{sign}", expire) == True:
                result = True, f"操作太频繁,请{expire}毫秒后再试"
        return result

    def check_attack_request(self):
        """
        :description: 攻击请求校验
        :return:满足条件直接拦截
        :last_editors: HuangJianYi
        """
        result = False, ""
        is_filter_attack = config.get_value("is_filter_attack", False)
        if is_filter_attack == True and self.request_params:
            for key in self.request_params.keys():
                if StringHelper.is_contain_sql(self.request_params[key]) or StringHelper.is_attack(self.request_params[key]):
                    result = True, f"参数{key}:值不合法"
                    break
        return result

    def get_signature_md5(self, request_param_dict, encrypt_key=""):
        """
        :description: 参数按照加密规则进行MD5加密
        :description: 签名规则 signature_md5= ((参数1=参数1值&参数2=参数2值&signature_stamp={signature_stamp}))+密钥)进行Md5加密转小写，参数顺序按照字母表的顺序排列
        :param request_param_dict: 请求参数字典
        :param encrypt_key: 接口密钥
        :return: 加密后的md5值，由于跟客户端传来的加密参数进行校验
        """
        request_sign_params = {}
        for k, v in request_param_dict.items():
            if k == "param_signature_md5":
                continue
            if k == "signature_md5":
                continue
            request_sign_params[k] = str(v).replace(" ", "_seven_").replace("(", "_seven1_").replace(")", "_seven2_")
        request_params_sorted = sorted(request_sign_params.items(), key=lambda e: e[0], reverse=False)
        request_message = "&".join(k + "=" + CodingHelper.url_encode(v) for k, v in request_params_sorted)
        request_message = request_message.replace("_seven_", "%20").replace("_seven1_", "(").replace("_seven2_", ")").replace("%27", "'")
        # MD5摘要
        request_encrypt = hashlib.md5()
        request_encrypt.update((request_message + str(encrypt_key)).encode("utf-8"))
        check_request_signature_md5 = request_encrypt.hexdigest().lower()
        return check_request_signature_md5

    def add_request_user(self, app_id, object_id):
        """
        :description: 每分钟流量UV计数,用于登录接口限制登录
        :param app_id: 应用标识
        :param object_id: 用户唯一标识
        :return:
        :last_editors: HuangJianYi
        """
        redis_init = SevenHelper.redis_init()
        cache_key = f"request_user_list_{app_id}:{str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M'))}"
        redis_init.sadd(cache_key, object_id)
        redis_init.expire(cache_key, 3600)

    def check_request_user(self, app_id, current_limit_count, current_limit_minute=1):
        """
        :description: 每分钟流量UV校验
        :param app_id: 应用标识
        :param current_limit_count: 流量限制数
        :param current_limit_minute: 流量限制时间，默认1分钟
        :return: True代表满足限制条件进行拦截
        :last_editors: HuangJianYi
        """
        if current_limit_count == 0:
            return False
        redis_init = SevenHelper.redis_init()
        if current_limit_minute == 1:
            cache_key = f"request_user_list_{app_id}:{str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M'))}"
        else:
            key_list = []
            for i in range(current_limit_minute):
                now_minute_int = int((datetime.datetime.now() + datetime.timedelta(minutes=-i)).strftime('%Y%m%d%H%M'))
                key = f"request_user_list_{app_id}:{str(now_minute_int)}"
                key_list.append(key)
            cache_key = f"request_user_list_{app_id}"
            redis_init.sinterstore(cache_key, key_list)
            redis_init.expire(cache_key, 3600)

        if int(redis_init.scard(cache_key)) >= current_limit_count:
            return True
        else:
            return False

    def get_app_key_secret(self):
        """
        :description: 获取app_key和app_secret
        :param 
        :return app_key, app_secret
        :last_editors: HuangJianYi
        """
        app_key = config.get_value("app_key")
        app_secret = config.get_value("app_secret")
        return app_key, app_secret

    def set_default_headers(self):
        """
        :description: 设置默认头部，用于跨域请求
        :return
        :last_editors: HuangJianYi
        """
        allow_origin_list = config.get_value("allow_origin_list")
        if not allow_origin_list:
            return
        origin = self.request.headers.get("Origin")
        if origin in allow_origin_list:
            self.set_header("Access-Control-Allow-Origin", origin)

        self.set_header("Access-Control-Allow-Headers", "Origin,X-Requested-With,Content-Type,Accept,User-Token,Manage-ProductID,Manage-PageID,PYCKET_ID")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")
        self.set_header("Access-Control-Allow-Credentials", "true")

    def get_user_nick(self):
        """
        :description: 获取用户昵称
        淘宝小程序 如果要在test和online环境指定账号打开后台测试，需由前端写死传入
        :return str
        :last_editors: HuangJianYi
        """
        user_nick = self.get_param("user_nick")
        #淘宝小程序 source_app_id在本地环境返回空；在test和online环境返回后端模板id，无论在IDE还是千牛端
        if self.get_param("source_app_id") == "":
            user_nick = config.get_value("test_user_nick")
        return user_nick

    def get_open_id(self):
        """
        :description: 获取open_id
        :return str
        :last_editors: HuangJianYi
        """
        open_id = self.get_param("open_id")
        if self.get_param("source_app_id") == "":
            open_id = config.get_value("test_open_id")
        return open_id

    def get_user_id(self):
        """
        :description: 获取user_id
        :param self
        :return str
        :last_editors: HuangJianYi
        """
        user_id = int(self.get_param("tb_user_id", 0))
        if user_id == 0:
            user_id = int(self.get_param("user_id", 0))
        return user_id

    def get_source_app_id(self):
        """
        :description: 获取source_app_id(客户端使用)
        :return str
        :last_editors: HuangJianYi
        """
        #当有参数app_id时，优先取app_id，然后在是source_app_id
        if self.get_param("app_id"):
            source_app_id = self.get_param("app_id")
            return source_app_id
        source_app_id = self.get_param("source_app_id")
        #淘宝小程序 在IDE上返回前端模板id，无论哪个环境；在千牛端上返回正确的小程序id
        if source_app_id == config.get_value("client_template_id") or source_app_id == "":
            source_app_id = config.get_value("test_source_app_id")
        return source_app_id

    def get_app_id(self):
        """
        :description: 获取app_id(后台使用)
        :param self
        :return str
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        if app_id == "":
            plat_type = config.get_value("plat_type", 1)  # 平台类型 1淘宝2微信3抖音
            user_nick = self.get_user_nick()
            if user_nick and plat_type == 1:
                store_user_nick = user_nick.split(':')[0]
                if store_user_nick:
                    app_info_dict = AppInfoModel(context=self).get_cache_dict(where="store_user_nick=%s", limit="0,1", field="app_id", params=store_user_nick)
                    if app_info_dict:
                        app_id = app_info_dict["app_id"]
        return app_id

    def create_operation_log(self, operation_type=1, model_name="", handler_name="", old_detail=None, update_detail=None, operate_user_id="", operate_user_name=""):
        """
        :description: 创建操作日志
        :param operation_type：操作类型：1-add，2-update，3-delete
        :param model_name：模块或表名称
        :param handler_name：handler名称
        :param old_detail：当前信息
        :param update_detail：更新之后的信息
        :param operate_user_id：操作人标识
        :param operate_user_name：操作人名称
        :return: 
        :last_editors: HuangJianYi
        """
        operation_log = OperationLog()
        operation_log_model = OperationLogModel(context=self)

        operation_log.app_id = ""
        operation_log.act_id = int(self.get_param("act_id", 0))
        operation_log.open_id = self.get_open_id()
        operation_log.user_nick = self.get_user_nick()
        operation_log.request_params = self.request_params
        operation_log.method = self.request.method
        operation_log.protocol = self.request.protocol
        operation_log.request_host = self.request.host
        operation_log.request_uri = self.request.uri
        operation_log.remote_ip = self.get_remote_ip()
        operation_log.create_date = TimeHelper.get_now_format_time()
        operation_log.operation_type = operation_type
        operation_log.model_name = model_name
        operation_log.handler_name = handler_name
        operation_log.detail = old_detail if old_detail else {}
        operation_log.update_detail = update_detail if update_detail else {}
        operation_log.operate_user_id = operate_user_id
        operation_log.operate_user_name = operate_user_name

        if isinstance(operation_log.request_params, dict):
            operation_log.request_params = self.json_dumps(operation_log.request_params)
        if isinstance(old_detail, dict):
            operation_log.detail = self.json_dumps(old_detail)
        if isinstance(update_detail, dict):
            operation_log.update_detail = self.json_dumps(update_detail)

        operation_log_model.add_entity(operation_log)

    def business_process_executing(self):
        """
        :description: 执行前事件
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = {}
        return invoke_result_data

    def business_process_executed(self, result_data, ref_params):
        """
        :description: 执行后事件
        :param result_data: result_data
        :param ref_params: 关联参数
        :return:
        :last_editors: HuangJianYi
        """
        return result_data


class ClientBaseHandler(FrameBaseHandler):
    """
    :description: 客户端handler基类
    """
    def prepare(self):
        """
        :Description: 置于任何请求方法前被调用(请勿重写此函数,可重写prepare_ext)
        :last_editors: HuangJianYi
        """
        if self.__class__.__name__ == "IndexHandler":
            return

        #获取并转换请求参数
        invoke_result_data = self._convert_request_params()
        if invoke_result_data.success == False:
            self.request_code = UUIDHelper.get_uuid()
            self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            self.finish()
            return

        try:
            # 标记日志请求关联
            dict_param = self.get_http_log_extra_dict()
            self._build_http_log(dict_param)

            # 获取设备信息
            self.device_info_dict = self.get_device_info_dict()

            # 防攻击校验
            is_attack_request, error_message = self.check_attack_request()
            if is_attack_request:
                self.response_json_error("error", error_message)
                self.finish()
                return

            # 验证超时 10分钟过期
            client_encrypt_type = config.get_value("client_encrypt_type", 0)
            server_encrypt_type = config.get_value("server_encrypt_type", 0)
            is_encrypt = False if hasattr(self, "is_encrypt") and self.is_encrypt == False else True
            if is_encrypt == True and ("/server/" in self.request.uri and server_encrypt_type == 1) or ("/client/" in self.request.uri and client_encrypt_type == 1):
                now_time = TimeHelper.get_now_timestamp(True)
                if self.request_params.__contains__("timestamp") and (now_time - int(self.request_params["timestamp"]) > int(1000 * 60 * 10)):
                    self.response_json_error("timestamp", "超时操作")
                    self.finish()
                    return

            # 频繁请求校验
            if dict_param["open_id"] and "/client/" in self.request.uri:
                is_continue_request, error_message = self.check_continue_request(self.__class__.__name__, dict_param["app_id"], dict_param["open_id"])
                if is_continue_request:
                    self.response_json_error("error", error_message)
                    self.finish()
                    return

                #每分钟流量UV计数,用于登录接口限制登录
                self.add_request_user(str(dict_param["app_id"]), str(dict_param["open_id"]))

        except Exception as ex:
            if not hasattr(self, "request_code"):
                self.request_code = UUIDHelper.get_uuid()
            self.logging_link_error("【客户端handler基类】" + traceback.format_exc())

    def get_online_url(self, act_id, app_id, module_id=0):
        """
        :description: 获取online_url
        :param act_id:活动标识
        :param app_id:应用标识
        :param module_id:模块标识
        :param page:跳转的首页地址pages/index/index
        :return str
        :last_editors: HuangJianYi
        """
        page_index = ""
        page = config.get_value("page_index")
        if page:
            page_index = "&page=" + CodingHelper.url_encode(page)
        query = CodingHelper.url_encode(f"actid={act_id}")
        if module_id > 0:
            query = CodingHelper.url_encode(f"actid={act_id}&module_id={module_id}")
        online_url = f"https://m.duanqu.com/?_ariver_appid={app_id}{page_index}&query={query}"
        return online_url

    def get_live_url(self, app_id):
        """
        :description: 获取live_url
        :param app_id:应用标识
        :return str
        :last_editors: HuangJianYi
        """
        live_url = f"https://market.m.taobao.com/app/taefed/shopping-delivery-wapp/index.html#/putin?mainKey=form&appId={app_id}"
        return live_url

    def get_device_info_dict(self):
        """
        :description: 获取头部参数字典
        :last_editors: HuangJianYi
        """
        device_info_dict = {}
        clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
        if clientheaderinfo_string:
            info_model = parse_qs(clientheaderinfo_string)
            device_info_dict["pid"] = int(info_model["pid"][0])  # 产品标识
            device_info_dict["chid"] = 0 if "chid" not in info_model.keys() else int(info_model["chid"][0])  # 渠道标识
            device_info_dict["height"] = 0 if "height" not in info_model.keys() else int(float(info_model["height"][0]))  # 高度
            device_info_dict["width"] = 0 if "width" not in info_model.keys() else int(float(info_model["width"][0]))  # 宽度
            device_info_dict["version"] = "" if "version" not in info_model.keys() else info_model["version"][0]  # 客户端版本号
            device_info_dict["app_version"] = "" if "app_version" not in info_model.keys() else info_model["app_version"][0]  # 小程序版本号
            device_info_dict["net"] = "" if "net" not in info_model.keys() else info_model["net"][0]  # 网络
            device_info_dict["model_p"] = "" if "model" not in info_model.keys() else info_model["model"][0]  # 机型
            device_info_dict["lang"] = "" if "lang" not in info_model.keys() else info_model["lang"][0]  #语言
            device_info_dict["ver_no"] = "" if "ver_no" not in info_model.keys() else info_model["ver_no"][0]  #接口版本号
            device_info_dict["timestamp"] = 0 if "timestamp" not in info_model.keys() else int(info_model["timestamp"][0])  # 时间搓毫秒
            device_info_dict["signature_md5"] = "" if "signature_md5" not in info_model.keys() else info_model["signature_md5"][0]  # 签名md5
        return device_info_dict

    def emoji_base64_to_emoji(self, text_str):
        """
        :description: 把加密后的表情还原
        :param text_str: 加密后的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        return CryptographyHelper.emoji_base64_to_emoji(text_str)

    def emoji_to_emoji_base64(self, text_str):
        """
        :description: emoji表情转为[em_xxx]形式存于数据库,打包每一个emoji
        :description: 性能遇到问题时重新设计转换程序
        :param text_str: 未加密的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        return CryptographyHelper.emoji_to_emoji_base64(text_str)


def filter_check_params(must_params=None):
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
            finally_must_params = must_params
            if hasattr(self, "must_params"):
                finally_must_params = self.must_params
            if type(finally_must_params) == str:
                must_array = finally_must_params.split(",")
            if type(finally_must_params) == list:
                must_array = finally_must_params

            if finally_must_params:
                for must_param in must_array:
                    if not must_param in self.request_params or self.request_params[must_param] == "":
                        self.response_json_error("param_error", "参数错误,缺少必传参数")
                        return

            return handler(self, **args)

        return wrapper

    return check_params


def filter_check_request(check_params=None):
    """
    :description: 请求过滤装饰器 仅限handler使用,
                    提供单用户是否存在对某一接口的达到指定请求数的持续请求的校验
                    装饰器使用方法:
                    @client_filter_check_params("param_a,param_b,param_c")  或
                    @client_filter_check_params(["param_a","param_b,param_c"])
    :param check_params: 校验参数集合
    :last_editors: HuangJianYi
    """
    def check_request(handler):
        def wrapper(self, **args):
            object_id = self.get_open_id()
            if not object_id:
                object_id = self.get_user_id()

            if self.request_params and object_id:

                app_id = self.get_app_id()
                if not app_id:
                    app_id = self.get_source_app_id()

                finally_check_params = []
                if type(check_params) == str:
                    finally_check_params = check_params.split(",")
                if type(check_params) == list:
                    finally_check_params = check_params
                if finally_check_params:
                    sign_params = {key: self.request_params[key] for key in self.request_params if key in finally_check_params}
                else:
                    sign_params = self.request_params
                redis_init = SevenHelper.redis_init()
                middle_key = f"{self.__class__.__name__}_{app_id}_{object_id}_{self.get_signature_md5(sign_params)}"
                if redis_init.get(f"check_request_limit:{middle_key}"):
                    self.response_json_error("request_error", "请求频繁,请稍后再试")
                    return
                cache_key = f"check_request_count:{middle_key}_{str(SevenHelper.get_now_int(fmt='%Y%m%d%H%M'))}"
                cache_value = redis_init.get(cache_key)
                if cache_value:
                    cache_value = int(cache_value)
                    if cache_value >= 30:
                        redis_init.set(f"check_request_limit:{middle_key}", 1, 60)
                        self.response_json_error("request_error", "请求频繁,请稍后再试")
                        return
                redis_init.incr(cache_key, 1)
                redis_init.expire(cache_key, 120)

            return handler(self, **args)

        return wrapper

    return check_request


def filter_check_head_sign(is_check=True, no_check_params=None):
    """
    :description: 头部过滤装饰器 仅限handler使用
    :param is_check: 是否开启校验
    :param no_check_params: 不加入参数校验的参数集合
    :last_editors: HuangJianYi
    """
    def check_head(handler):
        def wrapper(self, **args):
            encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
            is_check_head = config.get_value("is_check_head", False)
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
                    # 验证是否有设备信息
                    clientheaderinfo_string = self.request.headers._dict.get("Clientheaderinfo")
                    if clientheaderinfo_string:
                        # 将设备信息字符串转为字典类型
                        device_info_dict = self.device_info_dict(clientheaderinfo_string)
                        # 验证签名超时 10分钟过期
                        now_time = TimeHelper.get_now_timestamp(True)
                        if now_time - device_info_dict["timestamp"] > int(1000 * 60 * 10):
                            return self.response_json_error("timestamp", "超时操作")
                        # 验证是否有头部信息签名
                        if not device_info_dict.__contains__("signature_md5"):
                            return self.response_json_error("signature_md5", "缺少参数signature_md5")
                        # 验证头部签名是否成功
                        client_head_dict = dict([(k, v[0]) for k, v in parse_qs(clientheaderinfo_string, True).items() if not k in no_check_array])
                        head_signature_md5 = self.get_signature_md5(client_head_dict, encrypt_key)
                        signature_md5 = device_info_dict["signature_md5"].lower()
                        if signature_md5 != head_signature_md5:
                            return self.response_json_error("signature_fail", "头部签名验证失败")
                    else:
                        return self.response_json_error("no_device_info", "没有提交设备信息")
                except Exception as ex:
                    self.logging_link_error("【头部校验异常】" + traceback.format_exc())
                    return self.response_json_error("error", "头部验证失败")

            return handler(self, **args)

        return wrapper

    return check_head


def filter_check_params_sign(is_check=True, no_check_params=None):
    """
    :description: 请求参数过滤装饰器 仅限handler使用
    :param is_check: 是否开启校验
    :param no_check_params: 不加入参数校验的参数集合
    :last_editors: HuangJianYi
    """
    def check_params(handler):
        def wrapper(self, **args):
            encrypt_key = config.get_value("encrypt_key", "r8C1JpyAXxrFV26V")
            client_encrypt_type = config.get_value("client_encrypt_type", 0)
            server_encrypt_type = config.get_value("server_encrypt_type", 0)
            if ("/server/" in self.request.uri and server_encrypt_type != 2) or ("/client/" in self.request.uri and client_encrypt_type != 2):
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
                    # 验证参数
                    request_param_dict = {}
                    try:
                        if self.request.method == "POST" and "Content-Type" in self.request.headers and self.request.headers["Content-type"].lower().find("application/json") >= 0 and self.request.body:
                            request_param_dict = json.loads(self.request.body)
                        else:
                            request_param_dict = dict([(k, v[0]) for k, v in parse_qs(self.request.query, True).items() if not k in no_check_array])
                    except:
                        pass
                    if not request_param_dict.__contains__("param_signature_md5"):
                        return self.response_json_error("signature_fail", "缺少参数param_signature_md5")
                    check_request_signature_md5 = self.get_signature_md5(request_param_dict, encrypt_key)
                    param_signature_md5 = request_param_dict["param_signature_md5"].lower()
                    if check_request_signature_md5 != param_signature_md5:
                        return self.response_json_error("signature_fail", "参数签名验证失败")

                except Exception as ex:
                    self.logging_link_error("【请求参数校验异常】" + traceback.format_exc())
                    return self.response_json_error("error", "请求参数验证失败")

            return handler(self, **args)

        return wrapper

    return check_params
