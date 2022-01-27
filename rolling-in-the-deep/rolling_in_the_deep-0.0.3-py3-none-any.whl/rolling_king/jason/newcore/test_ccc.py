#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from src.rolling_king.jason.requests.http_sender_module import HttpSender

import json
import pytest


class TestCCCPlatform(object):

    def test_get(self):
        http_sender_obj = HttpSender("http://10.72.108.71:8080/")
        HttpSender.headers = {"header": "This is a customerized header"}
        input_param = {"groupName": "XY_CCC_GROUP"}
        http_sender_obj.send_get_request_by_suburi("meta/application.json", input_param)
        result_str = http_sender_obj.get_response.text
        print("结果：", result_str)
        dict_val = json.loads(result_str)
        print(type(dict_val))  # <class 'dict'>
        print(json.dumps(dict_val, indent=2))
        if "msg" in dict_val:
            msg_val = dict_val['msg']
            print("msg_val = {0}".format(msg_val))
            if msg_val == "success":
                assert 1
            else:
                assert 0
        else:
            assert 0


if __name__ == "__main__":
    pytest.main(["-s",  "test_ccc.py"])
