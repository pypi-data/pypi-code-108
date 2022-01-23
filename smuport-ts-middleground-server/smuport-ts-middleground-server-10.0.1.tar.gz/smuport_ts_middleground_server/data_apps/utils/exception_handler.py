# 注意，脚本路径需要与settings.py 定义的一样

from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        print('exception', response.data)
        response.data.clear()
        response.data['errCode'] = response.status_code
        response.data['data'] = []

        if response.status_code == 404:
            try:
                response.data['errMessage'] = response.data.pop('detail')
                # response.data['errMessage'] = "找不到资源"
            except KeyError:
                response.data['errMessage'] = "找不到资源"

        if response.status_code == 400:
            try:
                response.data['errMessage'] = response.data.pop('detail')
                # response.data['errMessage'] = "找不到资源"
            except KeyError:
                response.data['errMessage'] = "参数错误，请检查"

        elif response.status_code == 401:
            response.data['errMessage'] = "未授权"

        elif response.status_code >= 500:
            response.data['errMessage'] = "服务器错误"

        elif response.status_code == 403:
            response.data['errMessage'] = "资源不可用"

        elif response.status_code == 405:
            response.data['errMessage'] = '请求方式错误'
    # response.status_code = 200
    return response

# 无需调用，报错的时候他自己会调用！！
