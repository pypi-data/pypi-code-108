import subprocess
from quickspider.core.Node import BaseNode
from requests import Session
from scrapy import Selector


class xmuWebvpnSession(Session):
    login_page = "https://webvpn.xmu.edu.cn/login"
    def __init__(self, _username=None, _password=None):
        super().__init__()
        self._data = {
                "_username": _username, 
                "_password": _password
                }
        self.headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"}

    def _get_login_form(self, login_response):
        selector = Selector(text=login_response.text)
        captcha_id = selector.css("#captcha-wrap > div > div > input[type=hidden]::attr(value)").get()
        login_form = {
                "auth_type": "local",
                "username": self._data["_username"],
                "sms_code": "",
                "password": self._data["_password"],
                "captcha" : "",
                "needCaptcha": "false",
                "captcha_id" : captcha_id
                }
        return login_form
    
    def login(self):
        login_response = self.get(self.login_page)
        login_form = self._get_login_form(login_response)
        self.post(url="https://webvpn.xmu.edu.cn/do-login", json=login_form,)
        print("登录成功")


class xmuWebvpnNode(BaseNode):
    def __init__(self, _name, _username, _password):
        super().__init__(_name)
        self._session = xmuWebvpnSession(_username=_username,
                _password=_password)

    def init(self):
        self._session.login()

    def process_input(self, _input_url):
        _transformed_url = subprocess.run(["./portal.js", str(_input_url)],
                stdout=subprocess.PIPE).stdout.decode('utf8')[:-1]
        resp = self._session.get(_transformed_url)
        return resp

