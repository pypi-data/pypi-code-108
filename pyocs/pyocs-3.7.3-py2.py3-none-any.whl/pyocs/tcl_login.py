import requests
import re
import platform
import os
import json
import pathlib
import logging


class TclLogin(object):
    _login_url = "http://scbcrd.tclking.com:8080/oem/check"
    target_url = (
        "http://scbcrd.tclking.com:8080/oem/assets/css/bootstrap-select.css.map"
    )
    _cookies_file = ""
    _instance = None
    # 外部系统，用户、密码固定, 可以使用默认值
    _username = "xiejincai3122"
    _password = "xiejincai3122"
    _userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.62 Safari/537.36 Edg/81.0.416.31"
    _header = {
        "Origin": "null",
        "Host": "scbcrd.tclking.com:8080",
        "User-Agent": _userAgent,
        "Upgrade-Insecure-Requests": "1",
    }
    _session = requests.Session()

    _logger = logging.getLogger(__name__)
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    def __init__(self):
        self._logger.setLevel(level=logging.ERROR)
        if platform.system() == "Linux":
            home_dir = os.environ["HOME"]
            self._cookies_file = home_dir + "/.tcl_cookies"
            self._logger.info("run on linux")
        else:
            self._cookies_file = "tcl_cookies"
            self._logger.info("run on window")

    # 单例模式 singleton pattern
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TclLogin, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def get_account_from_json(self):
        if platform.system() == "Linux":
            home_dir = os.environ["HOME"]
            _account_json_file = home_dir + "/.account.json"
        else:
            _account_json_file = ".account.json"
        try:
            with open(_account_json_file, "r") as fd:
                account_dict = json.loads(json.dumps(eval(fd.read())))
                return account_dict
        except FileNotFoundError:
            self._logger.error('请创建登录账户的.account.json文件，{"Username":"xxx", "Password":"xxx"}')
            return None

    def login_by_post(self):
        r"""

        :return:
        """
        result = self._session.get(self._login_url, headers=self._header)
        reg = r'<input type="hidden" name="csrf_token" value="(.*)"/>'
        pattern = re.compile(reg)
        token_list = pattern.findall(result.content.decode("utf-8"))
        csrf_token = token_list[0] if token_list else None

        #使用公共账号登陆
        # account = self.get_account_from_json()
        # self._username = account['Username']
        # self._password = account['Password']
        post_data = {
            "csrf_token": csrf_token,
            "username": self._username,
            "password": self._password,
        }

        r = self._session.post(self._login_url, headers=self._header, data=post_data)
        server_cookies = self._session.cookies

        # self._logger.debug('cookies: ' + server_cookies)
        with open(self._cookies_file, "w") as fp:
            json.dump(requests.utils.dict_from_cookiejar(server_cookies), fp)
        self._logger.info("log in by post!")
        return r

    # @staticmethod
    def login_by_cookies(self, url=False):
        """
        :param url: request请求的连接
        :return:
        """
        tcl_cookies = self.get_login_cookies()
        self.target_url = url if url else self.target_url
        r = self._session.get(self.target_url, headers=self._header, cookies=tcl_cookies)
        if str(r.url) == self.target_url:
            self._logger.info("login by cookies successed!")
        else:
            self._logger.info("cookies is expired, try to login by post now...")
            return self.login_by_post()

        return r

    def get_login_cookies(self):
        r"""
        :rtype: dict
        """
        cookies_file = pathlib.Path(self._cookies_file)
        if not cookies_file.exists():
            self._logger.info("cookies is not exist! try to login by post now...")
            self.login_by_post()
        with open(self._cookies_file, "r") as fp:
            cookies = json.load(fp)
            return cookies
        pass

    pass


# if __name__ == "__main__":
#     t = TclLogin()
#     r = t.login_by_post()
#     print(r.text)
