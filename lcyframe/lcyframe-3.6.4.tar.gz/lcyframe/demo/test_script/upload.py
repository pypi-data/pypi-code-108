#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys, os
root_dir = os.path.dirname(os.path.dirname(__file__))
sys.path.append(root_dir)
from . import *
from lcyframe.libs import cprint

def upload():
    headers = {"uid": 100000}

    params = {

    }
    files = {"excel": open("Yijian_project/xxxxxxx.xlsx", "rb")}    # excel 是在yml定义的参数名

    return admin_login_and_send(
        methed="post",
        url="/upload",
        params=params,
        headers=headers,
        files=files
    )


if __name__ == "__main__":
    upload()

