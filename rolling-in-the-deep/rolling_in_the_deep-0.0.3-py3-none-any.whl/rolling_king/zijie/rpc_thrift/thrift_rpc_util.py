#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/3/8 3:26 下午
# @Author  : zhengyu.0985
# @FileName: thrift_rpc_util.py
# @Software: PyCharm

import thriftpy2
import os
from thriftpy2.rpc import make_aio_client, make_client


class ThriftUtil(object):
    BASE_DIR = ""
    THRIFT_PATH = ""

    def __init__(self, thrift_file_path, module_name):
        print("ThriftUtil Parameter Constructor has been called.")
        self.sync_task_thrift = thriftpy2.load(thrift_file_path, module_name=module_name)

    def get_sync_task_thrift(self):
        return self.sync_task_thrift

    @staticmethod
    def make_sync_client(service, ip, port):
        client = make_client(service, ip, port)
        return client


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(BASE_DIR)
    THRIFT_PATH = os.path.join(BASE_DIR, "tests/thrift/files", "union_account.thrift")
    print(THRIFT_PATH)
    thrift_util_obj = ThriftUtil(THRIFT_PATH, "UnionAccountService_thrift")
    sync_task_thrift = thrift_util_obj.get_sync_task_thrift()
    sync_client = ThriftUtil.make_sync_client(sync_task_thrift.UnionAccountService, '10.225.112.217', 9685)
    param = sync_task_thrift.QueryUserInfoRequest()
    param.CoreUserId = 140381073185863
    response = sync_client.QueryUserInfo(param)
    print(response)


