import requests
import logging
from pyocs import pyocs_login
from pyocs import pyocs_analysis
"""
# 封装一层request
1、可以用装饰器计算request请求消耗的时间
2、对应其他模块而言，使用更加方便，不用再理会登陆模块
"""


class PyocsRequest:
    _logger = logging.getLogger(__name__)
    _instance = None

    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别
        self._cookies = pyocs_login.PyocsLogin().get_login_cookies()

    # 单例模式
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(PyocsRequest, cls).__new__(cls, *args, **kw)
        return cls._instance

    @pyocs_analysis.PyocsAnalysis.print_run_time
    def pyocs_request_post(self, url, data, allow_redirects=False):
        return requests.post(url, data=data, cookies=self._cookies, allow_redirects=allow_redirects)

    def pyocs_request_post_file(self, url, file, header):
        return requests.post(url, files=file, cookies=self._cookies, headers=header)

    @pyocs_analysis.PyocsAnalysis.print_run_time
    def pyocs_request_post_with_headers(self, url, data, headers, allow_redirects=False):
        return requests.post(url, data=data, cookies=self._cookies, allow_redirects=allow_redirects, headers=headers)

    @pyocs_analysis.PyocsAnalysis.print_run_time
    def pyocs_request_get(self, url, allow_redirects=True):
        return requests.get(url, cookies=self._cookies, allow_redirects=allow_redirects)

    @pyocs_analysis.PyocsAnalysis.print_run_time
    def pyocs_request_post_json_with_headers(self, url, json, headers, allow_redirects=False, timeout=60):
        return requests.post(url, json=json, cookies=self._cookies, allow_redirects=allow_redirects, headers=headers, timeout=timeout)
