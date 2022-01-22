import os
import re
import pyDes
import requests  # https://github.com/kennethreitz/requests
import json
import base64
import logging
import platform
import getpass
...
# @author:zhubowen3432
# @作用：获取可以用于登陆的cookies
# @className：PyocsLogin
# @对外接口：get_login_cookies() 返回request需要的RequestsCookieJar类型的cookies
...


class PyocsLogin:
    # 全局信息
    _instance = None
    _logger = logging.getLogger(__name__)
    
    def __init__(self):
        self._logger.setLevel(level=logging.WARNING)  # 控制打印级别

    # 单例模式
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(PyocsLogin, cls).__new__(cls, *args, **kw)
        return cls._instance

    # 因为域账号统一，所以可以为其他系统提供账号，例如jenkins
    @staticmethod
    def get_account_from_json_file():
        key = "cvte2021"#密钥
        encrypt = True
        account_dict_encrypt = {}
        k = pyDes.des(key, pyDes.CBC, "00000000" , pad=None , padmode=pyDes.PAD_PKCS5)
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            _account_json_file = home_dir + '/.account.json'
        else:
            _account_json_file = 'account.json'
        try:
            logging.info(_account_json_file)
            with open(_account_json_file, 'r') as load_file:
                tmp = load_file.read()
                account_dict = json.loads(json.dumps(eval(tmp)))
                if re.match("^.*=$", account_dict["Username"]):
                    #存储的是密文
                    msg_decoded = PyocsLogin.decode_login_msg(k, account_dict["Username"], account_dict["Password"])
                    account_dict["Username"] = msg_decoded[0]; account_dict["Password"] = msg_decoded[1]
                else:
                    #存储的是明文
                    encrypt = False

                if ~encrypt:
                    #如果是明文存储，强制转换并将原来的明文替换掉
                    msg_encoded = PyocsLogin.encode_login_msg(k, account_dict["Username"], account_dict["Password"])
                    account_dict_encrypt["Username"] = msg_encoded[0]; account_dict_encrypt["Password"] = msg_encoded[1]

                    with open(_account_json_file, 'w') as load_file:
                        load_file.write(str(json.dumps(account_dict_encrypt, indent=4)))
                    encrypt = True

                return account_dict
        except FileNotFoundError:
            #logging.error("请创建JSON格式的文件，包含Username、Password值")
            username = input("请输入用户名（Username）: ")
            pw1 = "pw1"
            pw2 = "pw2"
            while pw1 != pw2:
                pw1 = getpass.getpass("请输入密码(Password) ： ")
                pw2 = getpass.getpass("请重复输入密码 ： ")
                if pw1 == pw2:
                    msg_encoded = PyocsLogin.encode_login_msg(k, username, pw1)
                    account_dict_encrypt["Username"] = msg_encoded[0];account_dict_encrypt["Password"] = msg_encoded[1]
                    with open(_account_json_file, 'w') as load_file:
                        load_file.write(str(json.dumps(account_dict_encrypt, indent=4)))
                    encrypt = True
                    break

            return {"Username" : username  , "Password" : pw1}

    @staticmethod
    def decode_login_msg(des, username, password):
        username_decoded = des.decrypt(base64.b64decode(username)).decode()
        password_decoded = des.decrypt(base64.b64decode(password)).decode()
        ##判断是否是+开头，如果是的话就去掉+
        if re.match("^\+", username_decoded):
            username_decoded = username_decoded[1:]
        return [username_decoded, password_decoded]

    @staticmethod
    def encode_login_msg(des, username, password):
        ##如果是3的整倍数的话，直接编码就不会有=号结尾
        ##所以强制加一个+号在开头
        if len(username) % 3 == 0:
            username = '+' + username
        username_encoded = str(base64.b64encode(des.encrypt(username)), encoding="utf-8")
        password_encoded = str(base64.b64encode(des.encrypt(password)), encoding="utf-8")
        return [username_encoded, password_encoded]

    def get_login_cookies(self):
        """
        :rtype: RequestsCookieJar
        """
        account = self.get_account_from_json_file()
        if account is None:
            return None

        return self.get_ocs_login_cookies(account['Username'], account['Password'])

    def get_login_cookies_str(self):
        """
        :rtype: RequestsCookieJar
        """
        account = self.get_account_from_json_file()
        if account is None:
            return None

        return self.get_ocs_login_cookies_str(account['Username'], account['Password'])

    @staticmethod
    def get_ocs_login_cookies(account, passwd):
        req = PyocsLogin.get_ocs_login_cookies_str(account, passwd)
        cookies_dict = json.loads(req)
        cookies = requests.utils.cookiejar_from_dict(cookies_dict)
        return cookies

    @staticmethod
    def get_ocs_login_cookies_str(account, passwd):
        _get_ocs_login_cookies_url = \
            "https://faas.gz.cvte.cn/function/get-ocs-login-cookies"
        headers = {
            "account": account,
            "passwd": passwd
        }
        req = requests.get(_get_ocs_login_cookies_url, headers=headers)
        return req.text