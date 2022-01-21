# -*- coding:utf-8 -*-
from lcyframe.libs.errors import ApiError as BaseError
from falcon.status_codes import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN


class ApiError(BaseError):
    code = 1
    code_name = 'Api Runtime Error'
    message = 'Runtime api error occurred.'
    status = HTTP_BAD_REQUEST

    def __init__(self, zh_message=None, code=None, code_name=None, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)
        if zh_message:
            self.zh_message = zh_message
        if code is not None:
            self.code = code
        if code_name is not None:
            self.code_name = code_name

    def to_dict(self, *args, **kwargs):
        return {
            'err_code': self.code,
            'err_name': self.code_name,
            'message': self.message
        }


# 非法请求
class ErrorInvalid(ApiError):
    """
    非法请求
    """
    code = 501
    code_name = 'invalid.'
    message = 'invalid request.'
    zh_message = '非法请求'
    help = "通常用于技术支持说明"

# 非法跨域
class ErrorCorsUri(ApiError):
    """
    非法请求
    """
    code = 502
    code_name = 'ErrorCorsUri'
    message = 'ErrorCorsUri'
    zh_message = '来自不授信的跨域请求'

# 参数类错误40x
class ErrorMissingArgument(ApiError):
    """
    参数缺失或错误
    """
    code = 503
    code_name = 'Missing Argument'
    zh_message = '参数缺失'


class ErrorArgumentType(ApiError):
    """
    参数类型错误
    """
    code = 504
    code_name = 'Argument Type Error'
    message = 'Argument Type Error'
    zh_message = '参数类型错误'

class ErrorArgumentValue(ApiError):
    """
    参数值错误
    """
    code = 505
    code_name = 'Argument Value Error'
    zh_message = '参数值不在允许范围'


# 返回类错误50x
class ErrorResponse(ApiError):
    """
    返回结构
    """
    code = 506
    code_name = 'Response Key Error!'
    zh_message = '返回结构与定义的不一致'


# 授权类错误 60x
class ErrorTokenInvalid(ApiError):
    """
    无效token
    """
    code = 601
    code_name = 'Invalid_Access_Token'
    message = 'Access token invalid.'
    zh_message = '无效的token'
    status = HTTP_FORBIDDEN

class ErrorTokenExpireInvalid(ApiError):
    """
    token已过期
    """
    code = 602
    code_name = 'Invalid_Access_Token'
    message = 'Access token expired.'
    zh_message = 'token已过期'
    status = HTTP_FORBIDDEN


class ErrorRefreshTokenInvalid(ApiError):
    code = 603
    code_name = 'Invalid_Refresh_Token'
    message = 'Refresh token invalid, refresh access-token failed.'
    zh_message = '请刷新token'
    status = HTTP_FORBIDDEN


# 权限类错误90x
class ErrorNoApiPermission(ApiError):
    """
    该账号没有调用该接口的权限
    """
    code = 901
    code_name = 'No_Api_Permission'
    message = 'No api permission'
    zh_message = '该账号没有调用该接口的权限'


class ErrorNoRolePermission(ApiError):
    """
    没有操作参数中角色或职位的权限
    """
    code = 902
    code_name = 'No_Role_Permission'
    message = 'No role permission'
    zh_message = '没有操作参数中角色或职位的权限'


class DemoObjectError(ApiError):
    """
    自定义错误对象
    """
    code = 1000
    code_name = 'DemoObjectError'
    message = 'DemoObjectError'
    zh_message = '自定义错误说明'

class ErrorSystemAPI(ApiError):
    """
    ******
    """
    code = 2000
    code_name = 'Api server is prohibition'
    zh_message = 'API服务暂停访问！'
    help = "系统升级中..."

