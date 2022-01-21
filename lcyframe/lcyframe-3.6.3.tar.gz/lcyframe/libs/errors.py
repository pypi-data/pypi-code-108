# -*- coding:utf-8 -*-
from falcon.status_codes import HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_FORBIDDEN


class ApiError(Exception):
    code = 1
    code_name = 'Api Runtime Error'
    message = 'Runtime api error occurred.'
    status = HTTP_BAD_REQUEST

    def __init__(self, message=None, code=None, code_name=None, *args, **kwargs):
        super(ApiError, self).__init__(*args, **kwargs)
        if message:
            self.message = message
        if code is not None:
            self.code = code
        if code_name is not None:
            self.code_name = code_name

    def to_dict(self, *args, **kwargs):
        print({
            'err_code': self.code,
            'err_name': self.code_name,
            'message': self.message
        })
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
    code = 2
    code_name = 'invalid.'
    message = 'invalid request.'
    zh_message = '非法请求'

# 非法跨域
class ErrorCorsUri(ApiError):
    """
    非法请求
    """
    code = 3
    code_name = 'ErrorCorsUri'
    message = 'ErrorCorsUri'
    zh_message = '来自不授信的跨域请求'

# 参数类错误40x
class ErrorMissingArgument(ApiError):
    """
    参数缺失或错误
    """
    code = 401
    code_name = 'Missing Argument'
    zh_message = '参数缺失'


class ErrorArgumentType(ApiError):
    """
    参数类型错误
    """
    code = 402
    code_name = 'Argument Type Error'
    message = 'Argument Type Error'
    zh_message = '参数类型错误'

class ErrorArgumentValue(ApiError):
    """
    参数值错误
    """
    code = 403
    code_name = 'Argument Value Error'
    zh_message = '参数值不在允许范围'


# 返回类错误50x
class ErrorResponse(ApiError):
    """
    返回结构
    """
    code = 501
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
    zh_message = ''
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


