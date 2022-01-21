#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from context import InitContext
from lcyframe.libs.singleton import MongoCon
from lcyframe.libs.cprint import cprint
from lcyframe.libs.JWT import JwtToken
import requests

config = InitContext.get_context()
db = MongoCon().get_database(**config["mongo_config"])
aes_secret = "******"
jwt_srcret = "******"
private_key = "-----BEGIN RSA PRIVATE KEY-----MIICYAIBAAKBgQDadqkuZj2A6gEW2HRKDgMX3XUfJp/NvA7ON2EUEJnBZQJ0Da8iFjqSnnu1fYHCBtDBC3m5b0xjBRQo91ZHYR9lHW5SAcWieoDWE/sYf6zsWiuJi8T7kum9oMyBAxjGhKD0HdGzYNN8+4f37wijbHR5mgFyzIdzmJPSXcUc+Zx4mQIDAQABAoGAako9ehPIbMZtjT33Jmi23I+lAmj6a1DKK08Kboa9KDkK/ogB46XJDbkKG31a+pnyS1pX+P7LvYmlC2F7JwRJjfSKGOAl34900o3rXK/55jbi+tUViruvEsZbJsM345FNSU4bf+Ct3ng1znrhrkuo76HUTw4FPzd3acb0AhHc7dkCRQDuSE9Gjq6WAO3w+1Fk6AzxVwTxiiLOVC5Ibc6wZWc3uwtncAmLm2S5TM6V/QCBuBDXHtzmppBVExbbHXHV7hiWsGsfDwI9AOq1GVjzKi5Dtr3dOpy7mhzX14TRGjS8gUZeQIBD0tmKLJKZEWkDA8rYMNLhA9IYMrOPb1+zMkXc1dRt1wJEGK4cp+43XwoRmxgswgrW7FhbBrmMCVrmwFG/Sr32Buu0rq4IDxG1SQwPibF+z/DErcNglfNCl802XNOb6tCSc2kqbzkCPGFIRwVTZLxgXLI9rDmimLIz1KS8dvw81ehw0JNZiV+ZoffxcgHwufWtvi7qDUdbuEgsv6EPCVtjuU2faQJFAIxj3I638xoF4AABzaVuxqBIMsacJOZhOH0Rbxo1oVVDkZ4uHa2GyoIAg7cDHzZqFV6GPa5qMa+Q0vH7GQjwwgJLU5WS-----END RSA PRIVATE KEY-----"
HEARDERS = {"appkey": ""}

def gen_token(uid, secret=jwt_srcret):
    return JwtToken(uid, secret).get_token()

def get_params(methed, docs):
    doc = docs[methed]
    params = {}

    if not doc:
        return params

    if isinstance(doc[0], dict):
        doc = doc[0].items()

    for k, v in doc:
        params[k] = v

    return params

def admin_login_and_send(methed, url, params, **kwargs):

    if "/" not in url:
        url = "/" + url

    global HEARDERS
    if "headers" not in kwargs:
        kwargs["headers"] = HEARDERS
    else:
        HEARDERS.update(kwargs["headers"])
        kwargs["headers"] = HEARDERS

    if "token" not in kwargs["headers"]:
        kwargs["headers"]["token"] = gen_token(kwargs["headers"].get("appkey")
                                               or kwargs["headers"].get("uid")
                                               or kwargs.get("agentid"))

    for k, v in kwargs["headers"].items():
        if isinstance(v, int):
            kwargs["headers"][k] = str(v)

    _url = config["wsgi"]["host"] #

    if "http" not in config["wsgi"]["host"]:
        _url = "http://" + _url + ":" + str(config["wsgi"]["port"])
    elif "127.0.0.1" in _url:
        _url = config["wsgi"]["host"] + ":" + str(config["wsgi"]["port"])
    _url += url


    if methed == "delete":
        kwargs["data"] = params
        data = eval("requests.%s" % methed)(_url, **kwargs)
    else:
        data = eval("requests.%s" % methed)(_url, params, **kwargs)

    r = data.json()

    # if r.status_code == 200:
    #     print(json.loads(r.content, encoding='utf-8'))
    # else:
    #     print(r.status_code, json.loads(r.content, encoding='utf-8'))

    cprint(r)
    return r

def get(url, params, **kwargs):
    admin_login_and_send("get", url, params, **kwargs)

def post(url, params, **kwargs):
    admin_login_and_send("post", url, params, **kwargs)

def put(url, params, **kwargs):
    admin_login_and_send("put", url, params, **kwargs)

def delete(url, params, **kwargs):
    admin_login_and_send("delete", url, params, **kwargs)

