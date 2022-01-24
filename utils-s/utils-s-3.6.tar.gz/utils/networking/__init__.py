from utils import _internal
_internal.depends.attemptImport(packagePythonName='requests', packagePip3Name='requests')
import requests


class requests_session:
    def __init__(self, optional_func=None, header=None):
        self.ses = requests.Session()
        self.function = optional_func
        self.const_head = header

    def get(self, url, headers=None):
        if headers is None:
            headers = self.const_head

        response = self.ses.get(url, headers=headers)
        if self.function is None:
            pass
        else:
            self.function(response)

        return response

    def post(self, url, data=None, json=None, headers=None):
        if headers is None:
            headers = self.const_head

        request = self.ses.post(url=url, data=data, json=json, headers=headers)
        if self.function is not None:
            self.function(request)

        return request

    def session(self):
        return self.ses

    def request(self, method, url, params=None, data=None, headers=None,
                cookies=None, files=None, auth=None, timeout=None,
                allow_redirects=True, proxies=None,
                hooks=None, verify=None,
                json=None):

        if headers is None:
            headers = self.const_head

        request = self.ses.request(url=url, method=method, proxies=proxies,
                                   params=params, data=data, headers=headers,
                                   cookies=cookies, files=files, auth=auth, timeout=timeout,
                                   allow_redirects=allow_redirects, hooks=hooks, verify=verify, json=json)

        if self.function is not None:
            self.function(request)

        return request

    def change_optional_func(self, function):
        self.function = function

    def change_constant_header(self, new_header):
        self.const_head = new_header


def waste():
    pass
