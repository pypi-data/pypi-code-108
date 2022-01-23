# 状态码
class ReturnCode:
    SUCCESS = 0
    FAILED = 100
    WRONG_PARAMS = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    RESOURCE_NOT_FOUND = 404
    SERVER_INTERNAL_ERROR = 500
    BROKEN_AUTHORIZED_DATA = 501
    SESSION_EXPIRED = 502
    UNKNOW_ERROR = 2000

    @classmethod
    def message(cls, code):
        if code == cls.SUCCESS:
            return 'success'
        elif code == cls.FAILED:
            return 'failed'
        elif code == cls.UNAUTHORIZED:
            return '未授权'
        elif code == cls.WRONG_PARAMS:
            return '错误请求'
        elif code == cls.FORBIDDEN:
            return '请求异常'
        elif code == cls.RESOURCE_NOT_FOUND:
            return '未找到资源'
        elif code == cls.BROKEN_AUTHORIZED_DATA:
            return '授权超时'
        elif code == cls.SERVER_INTERNAL_ERROR:
            return '服务器内部错误'
        elif code == cls.SESSION_EXPIRED:
            return '错误网关'
        elif code == cls.UNKNOW_ERROR:
            return '未知错误，请求异常！'


class CommonResponseMixin(object):
    @classmethod
    def wrap_json_response(cls, status=None,  data=None, code=None, message=None):
        response = {}
        if not code:
            code = ReturnCode.SUCCESS
        if not message:
            message = ReturnCode.message(code)
        if data:
            response['data'] = data
        response['errCode'] = code
        response['errMessage'] = message
        response
        return response
