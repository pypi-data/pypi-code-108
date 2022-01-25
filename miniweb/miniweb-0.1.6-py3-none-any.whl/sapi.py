import json
import functools

import bizerror
from .response import HttpResponse

def json_api(func):
    def wrapper(http_request, http_response):
        result = func(http_request, http_response)
        if not result and http_response.status_code != 200:
            return None
        if isinstance(result, HttpResponse):
            return result
        http_response.content_type = "application/json"
        http_response.content = json.dumps(result, ensure_ascii=False).encode("utf-8")

    return functools.wraps(func)(wrapper)

def jsonp_api(jsonp_field="jsonp"):
    def wrapper_outer(func):
        def wrapper(http_request, http_response):
            result = func(http_request, http_response)
            if not result and http_response.status_code != 200:
                return None
            if isinstance(result, HttpResponse):
                return result
            callback = http_request.GET.get(jsonp_field, "callback")
            http_response.content_type = "application/javascript"
            http_response.content = "{callback}({data});".format(callback=callback, data=json.dumps(result, ensure_ascii=False))
        return functools.wraps(func)(wrapper)
    return wrapper_outer

def simplejson_api(func):
    def wrapper(http_request, http_response):
        try:
            result = func(http_request, http_response)
            if not result and http_response.status_code != 200:
                return None
            if isinstance(result, HttpResponse):
                return result
            result = {
                "success": True,
                "result": result,
                "error": {
                    "code": 0,
                    "message": "OK",
                }
            }
        except Exception as error:
            error = bizerror.BizError(error)
            result = {
                "success": False,
                "result": None,
                "error": {
                    "code": error.code,
                    "message": error.message,
                }
            }
        http_response.content_type = "application/json"
        http_response.content = json.dumps(result, ensure_ascii=False).encode("utf-8")
    return functools.wraps(func)(wrapper)

def simplejsonp_api(jsonp_field="jsonp"):
    def wrapper_outer(func):
        def wrapper(http_request, http_response):
            try:
                result = func(http_request, http_response)
                if not result and http_response.status_code != 200:
                    return None
                if isinstance(result, HttpResponse):
                    return result
                result = {
                    "success": True,
                    "result": result,
                    "error": {
                        "code": 0,
                        "message": "OK",
                    }
                }
            except Exception as error:
                error = bizerror.BizError(error)
                result = {
                    "success": False,
                    "result": None,
                    "error": {
                        "code": error.code,
                        "message": error.message,
                    }
                }
            callback = http_request.GET.get(jsonp_field, "callback")
            http_response.content_type = "application/javascript"
            http_response.content = "{callback}({data});".format(callback=callback, data=json.dumps(result, ensure_ascii=False))
        return functools.wraps(func)(wrapper)
    return wrapper_outer
