import os
import time
import requests
from b_c_components.get_environment import get_environment_data

from b_c_components.custom_module.custom_exception import Configuration_file_error
from b_c_components.log.log import Logging
from selenium import webdriver
from b_c_components.get_config.get_config import Setting
from b_c_components.get_b_version.get_version import auto_get_browser_driver


import rsa
import base64
my_public_key = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCCAGUAYFFTqlMwndAkJbO6GoOiPTPMreeYJ6JfWbx5rliI4PevlmMZNISOtmZm6Sv44wlA4l+1y1wqAE31jPhH2bZ2qqbJdiPB7VXpR5nQeSZGcNCSCK7N62A5b8ssEjbWd5jMBiqD/erLkc87/jQ0iqd342Oixc9y4LFn//ABWwIDAQAB '


def str2key(s):
    # 对字符串解码
    b_str = base64.b64decode(s)
    if len(b_str) < 162:
        return False
    hex_str = ''

    # 按位转换成16进制
    for x in b_str:
        h = hex(x)[2:]
        h = h.rjust(2, '0')
        hex_str += h

    # 找到模数和指数的开头结束位置
    m_start = 29 * 2
    e_start = 159 * 2
    m_len = 128 * 2
    e_len = 3 * 2

    modulus = hex_str[m_start:m_start + m_len]
    exponent = hex_str[e_start:e_start + e_len]

    return modulus, exponent


def encrypt_framework(text):
    key = str2key(my_public_key)
    message = text.encode('utf-8')
    modulus = int(key[0], 16)
    exponent = int(key[1], 16)

    rsa_pubkey = rsa.PublicKey(modulus, exponent)
    crypto = rsa.encrypt(message, rsa_pubkey)
    b64str = base64.b64encode(crypto)
    return str(b64str, encoding="utf-8")


class v3_login_ui:
    """
    v3_ui_登陆
    """
    def __init__(self, driver=None):

        if driver is None:
            config_path = os.environ.get('config_path')
            self.setting = Setting(config_path)
            self.driver = webdriver.Chrome(auto_get_browser_driver(config_path))
        else:
            self.driver = driver
        if os.environ.get('environment'):
            self.url = get_environment_data(os.environ.get('environment')).get('tms_url')
        else:
            environment = self.setting.get_setting('environment_data', 'environment')
            if environment is None:
                raise Configuration_file_error(msg='配置文件不允许为空')
            self.url = get_environment_data(environment).get('tms_url')
        self.driver.get(self.url)

    def login_tms(self, app_name, username, password, entrance=True):
        """
        :param app_name:
        :param username:
        :param password:
        :param entrance:
        """
        username_element = '//*[@id="username"]'
        password_element = '//*[@id="password"]'
        login_element = '//*[@id="sub_btn"]'
        login_confirm = '//*[@id="confirm"]'
        login_confirm_button = '//*[@id="all_user_btn_save"]/span'

        self.driver.find_element_by_xpath(
            username_element).send_keys(username)
        self.driver.find_element_by_xpath(
            password_element).send_keys(password)
        self.driver.find_element_by_xpath('//*[@id="submit_checkbox"]').click()
        self.driver.find_element_by_xpath(login_element).click()
        time.sleep(1.5)
        login_confirm = self.driver.find_elements_by_xpath(login_confirm)
        if len(login_confirm) == 1 and login_confirm[0].is_displayed():
            self.driver.find_element_by_xpath(login_confirm_button).click()

        if entrance:
            apps_elements_str = '//*[@class= "buy_product clearfix"]/li'
            apps_elements = self.driver.find_elements_by_xpath(apps_elements_str)
            for i in range(len(apps_elements)):
                app_name_str = apps_elements_str + '[' + str(i + 1) + ']/div[2]/a'
                if app_name == self.driver.find_element_by_xpath(app_name_str).text:
                    apps_elements[i].click()
                    break
        return self.driver


class v3_login_interface:
    """
    v3接口登陆
    """

    @staticmethod
    def login_tms(username, password, environment):
        """

        :param username:
        :param password:
        :param environment:
        :return:
        """
        session = requests.session()
        login_data = {
            "UserName": f"{username}",
            "Password": f"{password}",
            "LoginType": "0",
            "Remember": "true",
            "IsShowValCode": "false",
            "ValCodeKey": ""}
        italent_url = get_environment_data(environment=environment).get('italent_url')
        r = session.post(url=italent_url + '/Account/Account/LogInITalent', data=login_data)
        if r.status_code == 200:
            url_dict = get_environment_data(environment=environment)
            session.get(url_dict.get('italent_url') + '/menuroute?roleId=&menuId=44629')
            return session
        else:
            return Configuration_file_error(msg=r.text)


if __name__ == '__main__':
    os.environ.setdefault('environment', 'prod')
    os.environ.setdefault('config_path', '/Users/sijunji/ProjectFile/PYObject/bs_ui_auto_c_c/unit_test/config_framework.ini')
    v3_login_ui().login_tms('测评', username='liyan410071@beisen.com', password='ly123456')
