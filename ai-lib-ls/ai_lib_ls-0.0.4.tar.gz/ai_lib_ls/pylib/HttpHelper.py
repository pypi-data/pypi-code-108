# 数据请求工具
import requests


class HttpRequsts:
    def get(self, url, params={}, headers={}):
        # 不包含任何参数的请求
        # r = requests.get(url_get)
        # # 不包含任何参数的请求,设置超时10s，timeout不设置则默认60s
        # r = requests.get(url_get, timeout=10)
        #
        # # 携带参数的请求，dict_param为参数字典
        # r = requests.get(url_get, data=dict_param)
        #
        # # 携带参数的请求，dict_param为参数字典，设置超时10s
        # r = requests.get(url_get, data=dict_param, timeout=10)

        # 携带参数的请求，dict_param为参数字典，设置超时10s,并携带headers属性
        # headers={ '参数 1'}

        return requests.get(url=url, params=params, headers=headers, timeout=10, verify=False)

    def post(self, url_post, dict_param, handers):
        # # 不包含任何参数的请求
        # r = requests.post(url_post)
        #
        # # 不包含任何参数的请求,设置超时10s，timeout不设置则默认60s
        # r = requests.post(url_post, timeout=10)
        #
        # # 携带参数的请求，dict_param为参数字典，默认data=dict_param，使用data=则表示post的是form请求，即 application/x-www-form-urlencoded 。
        # r = requests.post(url_post, data=dict_param)
        #
        # # 携带参数的请求，dict_param为参数字典，json=dict_param，使用json=则表示post的是json请求 。
        # r = requests.post(url_post, json=dict_param)
        #
        # # 携带参数的请求，dict_param为参数字典，data=json.dumps(dict_param)，则表示post的是json请求 。
        # r = requests.post(url_post, data=json.dumps(dict_param))
        #
        # # 携带参数的请求，dict_param为参数字典，设置超时10s
        # r = requests.post(url_post, data=dict_param, timeout=10)

        # 携带参数的请求，dict_param为参数字典，设置超时10s,并携带headers属性
        return requests.post(url_post, data=dict_param, timeout=10, headers=handers)

    def post_file(self, url_post, files):  # files = {'file': open('report.xls', 'rb')}
        # post请求上传文件
        return requests.post(url_post, files=files)
