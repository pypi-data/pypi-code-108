from copy import copy
from requests import Session
from scrapy import Selector
from quickspider.core.nodes import SessionNode
import encrypt


class DailyHealthSession(Session):
    """打卡客户端类"""
    url = {
        "login": ("https://ids.xmu.edu.cn/authserver/login?service="
                  "https://xmuxg.xmu.edu.cn/login/cas/xmu"),
    }
    clientHeaders = {
        "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0)"
                       " Gecko/20100101 Firefox/94.0")
    }
    data_login = {
        "username": "",
        "password": "",
        "lt": "",
        "dllt": "",
        "execution": "",
        "_eventId": "",
        "rmShown": "",
    }

    def __init__(self, _username, _password) -> None:
        super().__init__()
        self.headers.update(self.clientHeaders)
        self._is_login = False
        self._form = None
        self._username = _username
        self._password = _password

    @staticmethod
    def _encrypt_password(raw_password: str, salt: str) -> str:
        return encrypt.encrypt.encryptAES(raw_password, salt)

    def _build_login_data_from_resp(self, resp):
        # init
        data = copy(self.data_login)
        resp = Selector(text=resp.text)
        login_sec_box = resp.css("#casLoginForm input")
        salt = resp.css("#pwdDefaultEncryptSalt::attr(value)").get()
        # enumerate
        for _input in login_sec_box:
            name = _input.css("::attr(name)").get()
            value = _input.css("::attr(value)").get()
            if name and name in data.keys():
                data.update({name: value})
        # add more
        data["username"] = str(self._username)
        data["password"] = self._encrypt_password(str(self._password), salt)
        return data

    def _login(self):
        if self._is_login:
            print("已经登录")
            return
        # init session
        login_resp = self.get(self.url["login"])
        login_data = self._build_login_data_from_resp(login_resp)
        resp = self.post(self.url["login"],
                         data=login_data,
                         allow_redirects=True)
        print(resp.cookies)
        print("登录成功")
        self._is_login = True


class xmuLoginNode(SessionNode):
    def __init__(self, _name, _username, _password):
        super().__init__(_name, DailyHealthSession(_username, _password))
        self._username = _username
        self._password = _password

    def init(self):
        self._session._login()


