# 依赖包

import os
import requests  # https://github.com/kennethreitz/requests
import json
import logging
import platform

from pyocs.pyocs_logger import PyocsLogger


class CpsLogin:
    # 全局信息
    __Login_Address = "http://cps.cvte.com/users/login"  # cps登陆站点
    Access_URL = 'http://cps.cvte.com/'  # 任何你想要访问的cps站点
    _cookies_file = ""
    _str_Location = 'Location'
    _logger = ""

    def __init__(self):
        self._logger = PyocsLogger(name="CPS_UPLOAD_KEY").getPyocsLogger()
        self._logger.setLevel(level=logging.WARN)  # 控制打印级别

        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            self._cookies_file = home_dir + '/.cookies'
            self._logger.info("linux环境")
        else:
            self._cookies_file = 'cookies'
            self._logger.info("windows环境")

    @staticmethod
    def get_account_from_json_file(account_path):
        if platform.system() == "Linux":
            home_dir = os.environ['HOME']
            _account_json_file = home_dir + '/.account_' + str(account_path) + '_email.json'
        else:
            _account_json_file = 'C:/Users/CVTE/account_' + str(account_path) + '_email.json'

        try:
            with open(_account_json_file, 'r') as load_file:
                tmp = load_file.read()
                account_dict = json.loads(json.dumps(eval(tmp)))
                return account_dict
        except FileNotFoundError:
            logging.warning("请创建JSON格式的文件，包含Username、Password值")
            return None

    def get_login_cookies(self, account_path):
        """
        :rtype: RequestsCookieJar
        """

        # 获取本地存储的账号，并更新登录表单数据
        account = self.get_account_from_json_file(account_path=account_path)
        if account is None:
            return None

        form_data = dict()
        form_data.update({
            '_method': 'POST',
            'data[User][email]': account['Username'],
            'data[User][password]': account['Password'],
            'ProductBussiness': "1"
        })
        self._logger.info(form_data)

        headers = dict()
        headers.update({
            'User-Agent': "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3"
        })

        # 提交表单数据，登录
        session = requests.Session()
        login_response = session.post(url=self.__Login_Address, data=form_data, allow_redirects=False, headers=headers)
        self._logger.info("part 2 status code: " + str(login_response.status_code))
        self._logger.info("part 2 header: " + str(login_response.headers))
        self._logger.info(login_response.cookies)

        # 判断登录结果
        if (self._str_Location in login_response.headers) and (login_response.headers[self._str_Location.title()] == self.Access_URL):
            self._logger.warning('远程cookies登陆成功')
            return login_response.cookies
        else:
            self._logger.error('远程cookies登陆失败')
            return None

