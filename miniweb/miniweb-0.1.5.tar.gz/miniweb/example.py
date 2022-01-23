
from miniweb import Router
from miniweb import Application
from miniweb import json_api
from miniweb import simplejson_api

def plain_ping(http_request, http_response):
    return http_response.response("pong")

def plain_echo(http_request, http_response):
    msg = http_request.POST.get("msg", "")
    return http_response.response(msg)

def plain_redirect(http_request, http_response):
    return http_response.redirect("/plain/ping")

def plain_cookie(http_request, http_response):
    http_response.set_cookie("sessionid", "session01")
    http_response.set_cookie("appid", "app01")
    http_response.set_cookie("username", "username01")
    return http_response.response("cookie")

def plain_echo_cookie(http_request, http_response):
    msg = http_request.COOKIES.get("msg", "")
    return http_response.response(msg)

def plain_echo_payload(http_request, http_response):
    msg = http_request.PAYLOAD.get("msg", "")
    return http_response.response(msg)

def plain_get(http_request, http_response):
    field_name = http_request.GET.get("_field_name", "")
    if field_name:
        msg = http_request.GET.get(field_name, "")
    else:
        msg = ""
    return http_response.response(msg)

def plain_addflag(http_request, http_response):
    addflag = http_request.GET.get("addflag", "")
    if addflag:
        addflag += ",4"
    else:
        addflag = "4"
    http_request.GET["addflag"] = addflag
    return http_response.response(addflag)

plain_router = Router()
plain_router.add_route("/ping", plain_ping)
plain_router.add_route("/echo", plain_echo)
plain_router.add_route("/redirect", plain_redirect)
plain_router.add_route("/cookie", plain_cookie)
plain_router.add_route("/echo/cookie", plain_echo_cookie)
plain_router.add_route("/echo/payload", plain_echo_payload)
plain_router.add_route("/get", plain_get)
plain_router.add_route("/addflag", plain_addflag)

@json_api
def json_ping(http_request, http_response):
    return {
        "errorcode": "0",
        "errormsg": "OK",
        "data": "pong",
    }

@json_api
def json_echo(http_request, http_response):
    msg = http_request.GET.get("msg", "")
    return {
        "errorcode": "0",
        "errormsg": "OK",
        "data": msg,
    }

@json_api
def json_redirect(http_request, http_response):
    return http_response.redirect("/json/ping")

json_router = Router()
json_router.add_route("/ping", json_ping)
json_router.add_route("/echo", json_echo)
json_router.add_route("/redirect", json_redirect)


@simplejson_api
def simplejson_ping(http_request, http_response):
    return "pong"

@simplejson_api
def simplejson_echo(http_request, http_response):
    msg = http_request.GET.get("msg", "")
    return msg

@simplejson_api
def simplejson_redirect(http_request, http_response):
    return http_response.redirect("/simplejson/ping")

@simplejson_api
def simplejson_div(http_request, http_response):
    a = int(http_request.GET.get("a", "0"))
    b = int(http_request.GET.get("b", "0"))
    c = a / b
    return c

simplejson_router = Router()
simplejson_router.add_route("/ping", simplejson_ping)
simplejson_router.add_route("/echo", simplejson_echo)
simplejson_router.add_route("/redirect", simplejson_redirect)
simplejson_router.add_route("/div", simplejson_div)


class AddFlag1(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, http_request, http_response):
        addflag = http_request.GET.get("addflag", "")
        if addflag:
            addflag += ",1"
        else:
            addflag = "1"
        http_request.GET["addflag"] = addflag
        return self.get_response(http_request, http_response)

class AddFlag2(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, http_request, http_response):
        addflag = http_request.GET.get("addflag", "")
        if addflag:
            addflag += ",2"
        else:
            addflag = "2"
        http_request.GET["addflag"] = addflag
        return self.get_response(http_request, http_response)

class AddFlag3(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, http_request, http_response):
        addflag = http_request.GET.get("addflag", "")
        if addflag:
            addflag += ",3"
        else:
            addflag = "3"
        http_request.GET["addflag"] = addflag
        return self.get_response(http_request, http_response)


application = Application()
application.router.add_route("/plain", plain_router)
application.router.add_route("/json", json_router)
application.router.add_route("/simplejson", simplejson_router)
application.set_middlewares([
    AddFlag1,
    AddFlag2,
    AddFlag3,
])
