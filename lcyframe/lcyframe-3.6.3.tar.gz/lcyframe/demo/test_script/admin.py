#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from . import *
from lcyframe.libs import cprint

def login():
    headers = {"app_key": "******"}
    cprint.cprint(admin_login_and_send("post", "/admin/login",
               {"user_name": "admin",
                "pass_word": "123456",
                },
               headers=headers))

def create(user_name, nick_name):
    headers = {"uid": 100000}

    params = {
        "pass_word": "123456",  # "15076349690",
        "user_name": user_name,  # "******",
        "nick_name": nick_name,
        "sex": 1,
        "mobile": "13888888888",
        "email": "123@qq.com",
        "gid": 2
    }

    return admin_login_and_send(
        methed="post",
        url="/admin/member",
        params=params,
        headers=headers,
    )


if __name__ == "__main__":
    login()

