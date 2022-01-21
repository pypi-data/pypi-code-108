# -*- coding: utf-8 -*-
# author:chao.yy
# email:yuyc@ishangqi.com
# date:2021/11/9 4:47 下午
# Copyright (C) 2021 The lesscode Team

from typing import Tuple


class StatusCode:
    """
    StatusCode 统一请求返回状态码
    # A表示错误来源于用户，比如参数错误，用户安装版本过低，用户支付超时等问题；
    # B表示错误来源于当前系统，往往是业务逻辑出错，或程序健壮性差等问题；
    # C表示错误来源于第三方服务
    """

    def __init__(self, message=None):
        self.message = message

    # *响应服务请求的状态码与说明

    SUCCESS = ("00000", "请求成功")
    FAIL = ("99999", "请求失败")
    USER_VALIDATE_FAIL = ("A0001", "用户端错误")
    USER_REGISTER_FAIL = ("A0100", "用户注册错误")
    USER_NAME_VALIDATE_FAIL = ("A0110", "用户名校验失败")
    USER_NAME_EXIST = ("A0111", "用户名已存在")
    USER_NAME_INVALID = ("A0112", "用户名包含特殊字符")
    PHONE_ALREADY_REGISTER = ("A0113", "手机号已经注册")
    PASSWORD_VALIDATE_FAIL = ("A0120", "密码错误")
    PASSWORD_LENGTH_VALID = ("A0121", "密码长度不够")
    SHORT_MESSAGE_VALID_FAIL = ("A0130", "短信验证码错误")
    VALIDATE_CODE_ERROR = ("A0131", "验证码错误！")
    USER_LOGIN_EXCEPTION = ("A0200", "用户登录异常")
    USER_ACCOUNT_NOT_EXIST = ("A0201", "用户不存在")
    USER_ACCOUNT_EXPIRE = ("A0202", "账号已失效，请联系管理员！")
    USER_ACCOUNT_PASSWORD_EXPIRE = ("A0203", "密码已失效，请修改密码，重新登录")
    USER_ACCOUNT_EXCEEDED_ERRORS = ("A0204", "密码错误次数过多，账号已锁定，请稍后重试")
    USER_ACCOUNT_DORMANCY = ("A0205", "账号处于休眠状态，请联系管理员！")

    REQUEST_PARAM_ERROR = ("A0300", "用户请求参数错误")
    INVALID_USER_INPUT = ("A0301", "无效的用户输入")
    INSECURE_TRANSPORT_ERROR = ("A0302", "OAuth 2 必须使用 https.")
    INVALID_REQUEST_ERROR = ("A0303", "无效的请求")
    INVALID_CLIENT_ERROR = ("A0304", "无效客户端信息")
    INVALID_GRANT_ERROR = ("A0305", "无效授权类型")
    UNAUTHORIZED_CLIENT_ERROR = ("A0306", "未授权客户端信息")
    UNSUPPORTED_RESPONSE_TYPE_ERROR = ("A0307", "不支持的响应类型")
    UNSUPPORTED_GRANT_TYPE_ERROR = ("A0308", "不支持的授权类型")
    INVALID_SCOPE_ERROR = ("A0309", "请求的作用域无效、未知或格式不正确")
    ACCESS_DENIED_ERROR = ("A0310", "请求被拒绝")
    MISSING_AUTHORIZATION_ERROR = ("A0311", "请求HEADERS中缺少 AUTHORIZATION 参数")
    UNSUPPORTED_TOKEN_TYPE_ERROR = ("A0312", "不支持的TOKEN类型")
    MISSING_CODE_EXCEPTION = ("A0313", '请求响应中缺少 "CODE"')
    MISSING_TOKEN_EXCEPTION = ("A0314", '请求响应中缺少 "ACCESS_TOKEN"')
    MISSING_TOKEN_TYPE_EXCEPTION = ("A0315", '请求响应中缺少 "TOKEN_TYPE"')
    MISMATCHING_STATE_EXCEPTION = ("A0316", "CSRF告警！请求和响应中的状态不相等")

    # REQUIRED_PARAM_IS_EMPTY = ("A0310", "请求缺少必要参数:{}")
    @staticmethod
    def REQUIRED_PARAM_IS_EMPTY(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "A0320", "请求缺少必要参数:{}".format(message)

    INVALID_TIME_STAMP = ("A0321", "非法的时间戳参数")
    USER_INPUT_INVALID = ("A0322", "用户输入内容非法")
    VALIDATE_CODE_EXPIRE = ("A0400", "验证码过期")
    FORM_VALIDATE_FAIL = ("A0401", "表单校验失败")
    PARAM_VALIDATE_FAIL = ("A0402", "参数校验失败")
    PARAM_BIND_FAIL = ("A0403", "参数绑定失败")
    PHONE_NUM_NOT_FOUND = ("A0404", "找不到该用户，手机号码有误")

    # BUSINESS_FAIL = ("B0000", "{}")
    @staticmethod
    def BUSINESS_FAIL(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0000", "{}".format(message)

    ACCESS_DENIED = ("B0001", "访问权限不足")
    RESOURCE_DISABLED = ("B0002", "资源被禁用")
    RESOURCE_NO_AUTHORITY = ("B0003", "该资源未定义访问权限")
    RESOURCE_NOT_FOUND = ("B0404", "访问资源不存在")

    # INTERNAL_SERVER_ERROR = ("B0500", "服务器内部错误:{}")

    @staticmethod
    def INTERNAL_SERVER_ERROR(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0500", "服务器内部错误:{}".format(message)

    # RESOURCE_EXIST = ("B0501", "{}已存在,确保唯一性，不可重复")
    @staticmethod
    def RESOURCE_EXIST(message):
        """
        用于自定义消息提示信息
        :param message: 替换的消息内容
        :return:
        """
        return "B0501", "{}已存在,确保唯一性，不可重复".format(message)

    TIMEOUT = ("B0100", "系统执行超时")
    STRIKE_RECOVERY = ("B0200", "系统容灾系统被触发")
    RPC_INVOKE_ERROR = ("C0001", "调用第三方服务出错")
    SERVER_ERROR = ("C0002", "服务器内部错误")
    UNKNOWN_ERROR = ("C0003", "未知异常")
