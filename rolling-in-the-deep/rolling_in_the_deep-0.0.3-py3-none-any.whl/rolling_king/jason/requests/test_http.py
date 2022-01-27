#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from src.rolling_king.jason.requests.http_sender_module import HttpSender
import json
import pytest


class TestHttpPytest(object):

    def test_baidu(self):
        http_sender_obj = HttpSender('host')
        HttpSender.headers = {"header": "This is a customerized header"}
        # 下面一行用类名HttpSender调用方法，则self第一个参数需要传入相应对象。
        HttpSender.send_get_request(http_sender_obj, 'http://10.72.99.200:8080/query/interfaceListByModule.do?moduleName=customer')
        print("结果：", http_sender_obj.get_response.text)

    def test_baidu_with_set_header(self):
        http_sender_obj = HttpSender('host')
        http_sender_obj.set_headers({"header":"This is a customerized header"})
        # 下面一行用类HttpSender的对象http_sender_obj来调用方法，则self第一个参数不传。
        http_sender_obj.send_get_request('http://10.72.99.200:8080/query/interfaceListByModule.do?moduleName=customer')
        print("结果：", http_sender_obj.get_response.text)
        print("headers：", http_sender_obj.get_response.headers)

    def test_get(self):
        http_sender_obj = HttpSender("http://10.72.99.200:8080/")
        input_params = {"moduleName": "customer"}
        # 下面一行用类HttpSender的对象http_sender_obj来调用方法，则self第一个参数不传。
        http_sender_obj.send_get_request_by_suburi("query/interfaceListByModule.do", input_params)
        print("Text：", http_sender_obj.get_response.text)
        str_val = str(http_sender_obj.get_response.content)
        print("Content String：", str_val)
        left_index = str_val.index("[")
        right_index = str_val.index("]")
        content = str_val[left_index+1 : right_index]
        list_str = content.split(",")
        for curr_str in list_str:
            print("current value = %s" % curr_str[1:-1])

    def test_send_post_request(self):
        http_sender_obj = HttpSender("http://10.72.99.200:8080/")
        http_sender_obj.set_headers({"header":"This is a New customerized header for post request"})
        http_sender_obj.send_post_request("https://api.github.com/some/endpoint", json.dumps({'some': 'data'}))
        print("send_post_request response: %s" % http_sender_obj.post_response.text)
        http_sender_obj.send_post_request("https://api.github.com/some/endpoint", json.dumps({'some': 'data'}))
        print("Post Headers = {0}".format(http_sender_obj.post_response.headers))

    def test_send_json_post_request(self):
        http_sender_obj = HttpSender("http://10.72.99.200:8080/")
        http_sender_obj.send_json_post_request("https://api.github.com/some/endpoint", {'some': 'data'})
        print("send_json_post_request response: %s" % http_sender_obj.post_response.text)

    def test_send_json_post_request_with_headers_cookies(self):
        http_sender_obj = HttpSender("http://10.72.99.200:8080/")
        headers = {'content-type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
        cookies = {'key': 'value'}
        http_sender_obj.send_json_post_request_with_headers_cookies("https://api.github.com/some/endpoint", {'some': 'data'}, headers, cookies)
        print("send_json_post_request_with_headers_cookies response: %s" % http_sender_obj.post_response.text)
        print("字典类型,头信息=", http_sender_obj.post_response.headers)
        print("发送到服务器的头信息=", http_sender_obj.post_response.request.headers)
        print("返回cookie=", http_sender_obj.post_response.cookies)
        print("重定向信息=", http_sender_obj.post_response.history)


if __name__ == "__main__":
    pytest.main(["-s",  "test_http.py"])

# 上面为pytest的调用和测试，下面为直接测试。


# result = requests.get("http://10.72.99.200:8080/query/interfaceListByModule.do?moduleName=customer")
# print("结果：", result)
# print("Status：", result.status_code)
# print("Content：", result.content)
# strVal = str(result.content)
# print("Content String：", strVal)
# leftIndex = strVal.index("[")
# rightIndex = strVal.index("]")
# content = strVal[leftIndex+1 : rightIndex]
# listStr = content.split(",")
# for str in listStr:
#     print("current value = %s" % str[1:-1])


# sender = HttpSender()
# sender.send_get_request("http://10.72.99.200:8080/query/interfaceListByModule.do?moduleName=customer")
# print(sender.get_response)
# strVal = str(sender.get_response.content)

# senderNew = HttpSender("http://10.72.99.200:8080/")
# input_params = {"moduleName": "customer"}
# senderNew.send_get_request_by_suburi("query/interfaceListByModule.do", input_params)
# print("Text：", senderNew.get_response.text)
# strVal = str(senderNew.get_response.content)
# print("Content String：", strVal)
# leftIndex = strVal.index("[")
# rightIndex = strVal.index("]")
# content = strVal[leftIndex+1 : rightIndex]
# listStr = content.split(",")
# for str in listStr:
#     print("current value = %s" % str[1:-1])

# senderNew.send_post_request("https://api.github.com/some/endpoint", json.dumps({'some': 'data'}))
# print("send_post_request response: %s" % senderNew.post_response.text)

# senderNew.send_json_post_request("https://api.github.com/some/endpoint", {'some': 'data'})
# print("send_json_post_request response: %s" % senderNew.post_response.text)

# headers = {'content-type': 'application/json',
#            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}
# cookies = {'key': 'value'}
# senderNew.send_json_post_request_with_headers_cookies("https://api.github.com/some/endpoint", {'some': 'data'}, headers, cookies)
# print("send_json_post_request_with_headers_cookies response: %s" % senderNew.post_response.text)
# r.headers                                  #返回字典类型,头信息
# r.requests.headers                         #返回发送到服务器的头信息
# r.cookies                                  #返回cookie
# r.history                                  #返回重定向信息,当然可以在请求是加上allow_redirects = false 阻止重定向
# print("字典类型,头信息=", senderNew.post_response.headers)
# print("发送到服务器的头信息=", senderNew.post_response.request.headers)
# print("返回cookie=", senderNew.post_response.cookies)
# print("重定向信息=", senderNew.post_response.history)