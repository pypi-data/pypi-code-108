# coding=utf-8
from functools import wraps

import re
import types
from lcyframe.libs import utils
import logging

from lcyframe.libs import errors
from lcyframe.libs.JWT import JwtToken
import urllib

def authorize(method):
    @wraps(method)
    def check_token(self, *args, **kwargs):
        _check_token(self)
        return method(self, *args, **kwargs)

    return check_token


def _check_token(self):
    jwt = JwtToken(self.uid, self.application.token_config["secret"], self.application.token_config["expire"])
    try:
        if not jwt.is_validate(self.token):
            raise errors.ErrorTokenInvalid

        if jwt.is_expire(self.token):
            raise errors.ErrorTokenExpireInvalid

        payload = jwt.decode(self.token)
        if payload and payload["uid"] != self.uid:
            raise errors.ErrorTokenInvalid
    except Exception as e:
        raise errors.ErrorTokenInvalid


def admin(method):
    @wraps(method)
    def has_role(self, *args, **kwargs):
        uid = int(self.request.headers.get("uid", None) or 0)
        if not self.application.mongo.admin.find_one({"uid": int(uid)}):
            raise errors.ErrorInvalid

        return method(self, *args, **kwargs)

    return has_role


def params(permission_bit=0):
    def wrap(method):
        @wraps(method)
        def has_role(self, *args, **kwargs):
            self.params = get_params(self)
            if self.app_config.get("logging_config", {}).get("level", "debug") == "debug":
                logging.debug(self.params)

            uid = self.request.headers.get("uid", None) or 0
            if type(uid) != int and uid.isdigit():
                self.uid = int(uid)

            self.token = self.request.headers.get("token", "")

            token_debug = self.token_config.get("debug", False)
            if not token_debug:
                if permission_bit != 0:
                    if not self.uid or not self.token:
                        raise errors.ErrorTokenInvalid

                    _check_token(self)

            return method(self, *args, **kwargs)

        return has_role

    return wrap


def get_params(self, fill_default=True):

    p = {}
    method = self.request.method.lower()

    if not self.request.arguments:
        try:
            body_arguments = {k: v for k, v in
                              [item.split("=") for item in self.request.body.decode().split("&")]}
        except Exception as e:
            body_arguments = {}
    else:
        body_arguments = self.request.arguments

    if not self.request.files:
        files = {}
    else:
        files = self.request.files

    params_mp = {}
    if self.request.path in self.application.api_schema_mp:
        params_mp = self.application.api_schema_mp[self.request.path].get("method", {})
    else:
        # from tornado.routing import RuleRouter, PathMatches, _unquote_or_none
        for route in self.application.handlers:
            match = route.regex.match(self.request.path)        # ref: routing.PathMatches.match
            if match is not None:
                pattern1 = route.regex.pattern
                pattern2 = route.regex.pattern.rstrip("$")
                if pattern1 in self.application.api_schema_mp:
                    params_mp = self.application.api_schema_mp[pattern1].get("method", {})
                elif pattern2 in self.application.api_schema_mp:
                    params_mp = self.application.api_schema_mp[pattern2].get("method", {})
                else:
                    params_mp = {}

                # path_args = [_unquote_or_none(s) for s in match.groups()]
                break

    if method in params_mp:
        for item in params_mp[method].get("parameters", []) or []:
            params_name = item["name"]
            _type = item["type"]

            if _type is [True, False, None]:
                # raise errors.ErrorArgumentType
                msg = "Argument '%s' Type can not is bool." % params_name
                e = errors.ErrorArgumentType
                e.message = msg
                raise e

            required = item.get("required", False)

            regex = item.get("regex")
            allow = item.get("allow", []) or item.get("allowed", [])
            message = item.get("message", "")

            if item.get("in") is None:
                if self.request.arguments:
                    if item["type"] == "list":
                        # 参数为数组
                        params_vaule = self.get_arguments(params_name) or None
                    else:
                        params_vaule = self.get_argument(params_name, None, strip=True)
                else:
                    if not body_arguments:
                        raise errors.ErrorArgumentValue

                    params_vaule = body_arguments.get(params_name)
                    try:
                        if params_vaule:
                            params_vaule = urllib.parse.unquote(params_vaule)
                    except Exception as e:
                        msg = "Argument '%s' Value '%s' Error" % (params_name, params_vaule)
                        e = errors.ErrorArgumentValue
                        e.message = msg
                        raise e
            else:
                _in = item.get("in", "query")
                if _type in ["file", "files"]:
                    _in = item.get("in", "form-data")

                if _in in ["query"]:
                    if item["type"] == "list":
                        # 参数为数组
                        params_vaule = self.get_arguments(params_name) or None
                    else:
                        params_vaule = self.get_argument(params_name, None, strip=True)

                elif _in in ["www-form", "body-form"]:
                    if item["type"] == "list":
                        # 参数为数组
                        params_vaule = self.get_arguments(params_name) or None
                    else:
                        params_vaule = self.get_argument(params_name, None, strip=True)

                elif _in in ["body-json"]:
                    if self.request.arguments:
                        if item["type"] == "list":
                            # 参数为数组
                            params_vaule = self.get_arguments(params_name) or None
                        else:
                            params_vaule = self.get_argument(params_name, None, strip=True)
                    else:
                        if self.request.body:
                            body_arguments = {k: v for k, v in [item.split("=") for item in self.request.body.decode().split("&")]}
                        else:
                            body_arguments = {}

                        params_vaule = body_arguments.get(params_name)
                        try:
                            if params_vaule:
                                params_vaule = urllib.parse.unquote(params_vaule)
                        except Exception as e:
                            msg = "Argument '%s' Value '%s' Error" % (params_name, params_vaule)
                            e = errors.ErrorArgumentValue
                            e.message = msg
                            raise e

                elif _in in ["form-data"]:
                    if item["type"] == "list":
                        # 参数为数组
                        params_vaule = self.get_arguments(params_name) or None
                    elif item["type"] in ["files", "file"]:
                        _type = "dict"
                        if params_name not in files:
                            params_vaule = None
                        else:
                            params_vaule = files[params_name][0]
                    else:
                        params_vaule = self.get_argument(params_name, None, strip=True)

                elif _in in ["binary"]:
                    msg = "参数：'%s'，不再支持将参数位置设置为binary方式" % params_name
                    e = errors.ErrorArgumentValue
                    e.message = msg
                    raise e
                    _type = "str"
                    params_vaule = self.request.body

                else:
                    # raise errors.ErrorArgumentType
                    msg = "Missing Argument '%s'. must in [query, form-data, www-form, file]." % params_name
                    e = errors.ErrorMissingArgument
                    e.message = msg
                    raise e

            if params_vaule is None:
                if required is True:  # 必传
                    msg = "Missing Argument '%s'" % params_name
                    e = errors.ErrorMissingArgument
                    e.message = msg
                    raise e

                if not fill_default:
                    continue

                # 客户端没有传值, 按照默认值类型赋值
                # params_vaule = default() if isinstance(default, types.FunctionType) or isinstance(default, types.TypeType) else default
                if item.get("default") is not None:
                    params_vaule = item.get("default")
                else:
                    continue

            else:
                # 按照默认值的类型 转换参数
                try:
                    params_vaule = utils.TypeConvert.convert_params(_type, params_vaule)
                except Exception as e:
                    # raise errors.ErrorArgumentType
                    msg = "Argument '%s' Type Error, Require '%s'" % (params_name, _type)
                    e = errors.ErrorArgumentType
                    e.message = msg
                    raise e

                if allow and params_vaule not in allow:
                    msg = "Argument '%s' must be in %s" % (params_name, utils.to_json(allow))
                    e = errors.ErrorArgumentValue
                    e.message = message or msg
                    raise e

                if regex and params_vaule is not None and not re.match(r"%s" % regex, str(params_vaule)):
                    # raise errors.ErrorArgumentValue
                    msg = "Argument '%s' Value does not match expression" % params_name
                    e = errors.ErrorArgumentValue
                    e.message = message or msg
                    raise e

            p[params_name] = params_vaule

    return p


def parse_vals(response_key, response, definition):
    t = type(definition)
    if t not in [str]:
        try:
            return t(response)
        except Exception as exc:
            e = errors.ErrorResponse()
            e.message = "KEY '%s' type is Error in Reference .yml response definition! error.message=%s" % (
                response_key, exc.args[0])
            logging.warning("=== response_key: %s, response: %s ===" % (response_key, response))
            raise e

    for _type in utils.TypeConvert.STR2TYPE.keys():
        value_type = "|%s" % _type
        if value_type in definition and definition.split("|")[-1] == _type:
            try:
                response = utils.TypeConvert.MAP[utils.TypeConvert.STR2TYPE[_type]](response)
            except ValueError as e:
                e = errors.ErrorResponse()
                e.message = "Key '%s' type in response must is %s. Reference .yml response definition!" % (
                    response_key, type(definition))
                raise e
            break

    return response


def recursion(response, definition, force_return=False):
    p = {}
    l = []
    is_dict = True

    e = errors.ErrorResponse()
    if type(response) != type(definition):
        try:
            response = response.encode("u8")
            definition = definition.encode("u8")
        except:
            e.message = "Response Key '%s' data type != .yml response definition!" % utils.to_json(response)
            raise e
            # raise TypeError("Response data type != .yml response definition!")

    if type(definition) is dict:
        for k, v in definition.items():
            k = str(k)
            if k not in response:
                if force_return:
                    e.message = "Key '%s' not in response data. Reference .yml response definition!" % k
                    raise e
                    # raise KeyError("Key %s not in your response data. Reference .yml response definition!" % k)
                else:
                    continue

            # if type(response[k]) in [dict, list, tuple] and type(v) not in [dict, list, tuple]:
            #     e.message = "response Key '%s' must be the same in Reference .yml response definition!" % (k, type(v), type(response[k]))
            #     raise e
            #
            # if type(v) in [dict, list, tuple] and type(response[k]) not in [dict, list, tuple]:
            #     e.message = "response Key '%s' must be the same in Reference .yml response definition!" % (k, type(v), type(response[k]))
            #     raise e

            if type(v) in [dict, list, tuple]:
                if type(response[k]) != type(v):
                    e.message = "Key '%s' in response must is %s. Reference .yml response definition!" % (
                        k, type(v))
                    raise e
                # p[k] = response[k]
                p[k] = recursion(response[k], v, force_return)
            else:
                p[k] = parse_vals(k, response[k], v)
    else:
        is_dict = False
        for index, d in enumerate(response):
            if type(d) not in [dict, list, tuple]:
                l.append(d)
            else:
                is_same_type = True
                first_type = type(definition[0])
                for item in definition:
                    if type(item) != first_type:
                        is_same_type = False
                        break

                # 列表的项类型相同，推荐
                if is_same_type:
                    l.append(recursion(d, definition[0], force_return))
                # 各项类型不相同，需要定义的长度和返回的一致
                elif len(response) == len(definition):
                    l.append(recursion(d, definition[index], force_return))
                else:
                    raise
    return p if is_dict else l


# def recursion(response, definition, force_return=False):
#     """
#     definition: 1
#     definition: s
#     definition: [1, s, [], {}]
#     definition: {k: 1, k: s, k: [], k: {}}
#     :param response:
#     :param definition:
#     :param force_return:
#     :return:
#     """
#     return_data = {}
#     return_dict = {}
#     return_list = []
#     return_static = ""
#     r_type = type(response)
#     d_type = type(definition)
#     e = errors.ErrorResponse()
#
#     check_type(response, definition)
#
#     if d_type is dict:
#         for k, v in definition.items():
#             k = str(k)
#             if k not in response:
#                 if force_return:
#                     e.message = "Key '%s' not in response data. Reference .yml response definition!" % k
#                     raise e
#                 else:
#                     continue
#
#             try:
#                 response[k] = response[k].encode("u8")
#                 v = v.encode("u8")
#             except:
#                 pass
#
#             if type(response[k]) != type(v) and "|" not in v:
#                 e.message = "Key '%s' in response must is %s. Reference .yml response definition!" % (
#                     k, type(v))
#                 raise e
#
#             return_data[k] = recursion(response[k], v, force_return)
#
#     elif d_type in [list, tuple]:
#         # 列表里设置的每个项类型相同
#         is_same_type = True
#         first_type = type(definition[0])
#         for item in definition:
#             if type(item) != first_type:
#                 is_same_type = False
#                 break
#
#         # 各项类型不相同，需要定义的长度和返回的一致
#         if not is_same_type and len(response) != len(definition):
#             e.message = "definition list is_same_type and length != response. Reference .yml"
#             raise e
#
#         for i, v in enumerate(response):
#
#             if is_same_type:
#                 return_list.append(recursion(v, definition[0], force_return))
#             else:
#                 return_list.append(recursion(v, definition[i], force_return))
#     else:
#         return_static = parse_vals(response, response, definition)
#
#     return return_data if return_data else return_list if return_list else return_static
#
#
# def check_type(response, definition):
#     r_type = type(response)
#     try:
#         definition, t_type = definition.split("|")
#     except:
#         t_type = None
#
#     if t_type and t_type in utils.TypeConvert.STR2TYPE:
#         d_type = utils.TypeConvert.STR2TYPE[t_type]
#     else:
#         d_type = type(definition)
#
#     if r_type != d_type:
#         try:
#             response = response.encode("u8")
#             definition = definition.encode("u8")
#         except:
#             e.message = "Response Key '%s' data type != .yml response definition!" % utils.to_json(response)
#             raise e
#
def get_return(self, response):
    method = self.request.method.lower()
    path = self.request.path
    api_schema_mp = self.application.api_schema_mp
    if path not in api_schema_mp or method not in api_schema_mp[path]["method"]:
        return response

    if not api_schema_mp[path]["method"].get(method):
        return response

    definition = api_schema_mp[path]["method"][method].get("responses")
    if not definition:
        return response

    p = recursion(response, definition, self.application.api_docs.get("force_return", False))
    return p