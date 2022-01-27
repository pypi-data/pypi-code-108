

import socket
import time
import zipfile
import requests
import sys
import os
from biplist import *
from b_c_components.get_config.get_config import Setting


def auto_get_browser_driver(config_path):
    """
    aaaa
    """
    if sys.platform == "darwin":
        plist_path = Setting(config_path).get_setting('mac_browser_plist_path', 'chrome_list_path')
        plist = readPlist(plist_path)
        # plist = readPlist(
        #     r"/Applications/Google Chrome.app/Contents/Info.plist")
        b_big_version = plist['KSVersion'].split(".")[0]
        if b_big_version not in os.listdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '/driver/mac/chrome/'):
            os.mkdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '/driver/mac/chrome/' +
                b_big_version)
            time.sleep(5)
        if 'chromedriver' not in os.listdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '/driver/mac/chrome/' + b_big_version + '/'):
            print(b_big_version)
            # 确认平台文件名称 http://chromedriver.storage.googleapis.com/index.html
            # 下载URL  https://chromedriver.storage.googleapis.com/86.0.4240.22/chromedriver_mac64.zip
            # mac chromedriver_mac64.zip win chromedriver_win32.zip

            b_version_complete = requests.get(
                'http://npm.taobao.org/mirrors/chromedriver/LATEST_RELEASE_' +
                b_big_version).text
            url = 'http://npm.taobao.org/mirrors/chromedriver/' + \
                  b_version_complete + '/chromedriver_mac64.zip'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
            Chrome/78.0.3904.87 Safari/537.36'}
            filename = os.path.dirname(os.path.dirname(__file__)) + '/driver/mac/chrome/' + b_big_version
            r = requests.get(url, headers, timeout=30)
            with open(filename + "/chromedriver.zip", "wb") as code:
                code.write(r.content)
            unzip_file(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '/driver/mac/chrome/' +
                b_big_version +
                r'/chromedriver.zip',
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '/driver/mac/chrome/' +
                b_big_version)
        return os.path.dirname(os.path.dirname(__file__)) + '/driver/mac/chrome/' + b_big_version + "/chromedriver"
    if sys.platform == "win32":
        import winreg
        hostname = socket.gethostname()
        if hostname == 'BYVW-WEB-40-28':
            file_path = Setting(config_path).get_setting('windows_browser_path', 'service_chrome_browser_path')
        else:
            file_path = Setting(config_path).get_setting('windows_browser_path', 'chrome_browser_path')
        # 判断路径文件是否存在
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"{file_path} is not found.")
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Google\Chrome\BLBeacon')
        b_big_version = winreg.QueryValueEx(key, 'version')[0].split('.')[0]



        if b_big_version not in os.listdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '\\driver\\win\\chrome\\'):
            os.mkdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '\\driver\\win\\chrome\\' +
                b_big_version)
        if 'chromedriver.exe' not in os.listdir(
                os.path.dirname(
                    os.path.dirname(__file__)) +
                '\\driver\\win\\chrome/' + b_big_version + '\\'):
            b_version_complete = requests.get(
                'http://npm.taobao.org/mirrors/chromedriver/LATEST_RELEASE_' +
                b_big_version).text
            url = 'http://npm.taobao.org/mirrors/chromedriver/' + \
                  b_version_complete + '/chromedriver_win32.zip'

            def requestDemo(driver_url, times=1):
                """

                :param driver_url:
                :param times:
                :return:
                """
                header = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)\
                    Chrome/78.0.3904.87 Safari/537.36'}
                try:
                    return requests.get(driver_url, headers=header, timeout=3)
                except BaseException:
                    trytimes = 3  # 重试的次数
                    if times < trytimes:
                        times += 1
                        return requestDemo(driver_url, times)
                return 'out of maxtimes'

            r = requestDemo(url)
            filename = os.path.dirname(os.path.dirname(__file__)) + r'\driver\win\chrome\\' + b_big_version
            with open(filename + "/chromedriver.zip", "wb") as code:
                code.write(r.content)

            unzip_file(os.path.join(
                    os.path.dirname(
                        os.path.dirname(__file__)),'driver','win','chrome',b_big_version,'chromedriver.zip')
                ,
                os.path.dirname(
                    os.path.dirname(__file__)) +
                r'\driver\win\chrome\\' + b_big_version)
        return os.path.dirname(os.path.dirname(__file__)) + '/driver/win/chrome/' + b_big_version + "/chromedriver.exe"


def unzip_file(zip_src, dst_dir):
    """

    :param zip_src:
    :param dst_dir:

    """
    if sys.platform == "darwin":
        os.system('unzip ' + zip_src)
        os.system('mv chromedriver ' + dst_dir)
    if sys.platform == "win32":
        with zipfile.ZipFile(zip_src, 'r') as zip_ref:
            zip_ref.extractall(dst_dir)
    if sys.platform == 'linux':
        os.system('unzip ' + zip_src)
        os.system('mv chromedriver ' + dst_dir)
    os.remove(zip_src)
