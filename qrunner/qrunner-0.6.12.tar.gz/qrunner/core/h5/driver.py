import os
import time

import allure
import requests
from selenium import webdriver
from qrunner.utils.config import conf
from qrunner.utils.log import logger
from qrunner.utils.webdriver_manager_extend import ChromeDriverManager


# 重启chromedriver的装饰器
def relaunch(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except requests.exceptions.ConnectionError as _:
            logger.warning("h5 driver error, relaunch now.")
            self.d = H5Driver(conf.get_name('app', 'serial_no'))
    return wrapper


class H5Driver(object):
    _instance = {}

    def __new__(cls, serial_no=None):
        if not serial_no:
            serial_no = conf.get_name('app', 'serial_no')
        if serial_no not in cls._instance:
            cls._instance[serial_no] = super().__new__(cls)
        return cls._instance[serial_no]

    def __init__(self, serial_no=None, pkg_name=None):
        if not serial_no:
            serial_no = conf.get_name('app', 'serial_no')
        if not pkg_name:
            pkg_name = conf.get_name('app', 'pkg_name')

        logger.info(f'启动H5Driver for {serial_no}')
        options = webdriver.ChromeOptions()
        # options.add_experimental_option('androidDeviceSerial', serial_no)
        options.add_experimental_option('androidPackage', pkg_name)
        options.add_experimental_option('androidUseRunningApp', True)
        # options.add_experimental_option('androidProcess', pkg_name)
        version = conf.get_name('app', 'webview')
        self.d = webdriver.Chrome(
            executable_path=ChromeDriverManager(version=version).install(),
            options=options
        )
        self.d.set_page_load_timeout(60)

    @staticmethod
    def get_instance(cls, serial_no=None):
        if serial_no not in cls._instance:
            logger.info(f'{serial_no} Create h5 driver singleton')
            return H5Driver(serial_no)
        return H5Driver._instance[serial_no]

    @relaunch
    def open_url(self, url):
        logger.info(f'访问: {url}')
        self.d.get(url)

    @relaunch
    def back(self):
        logger.info('返回上一页')
        self.d.back()

    @relaunch
    def screenshot(self, file_name):
        """
        截图并保存到预定路径并上传到allure报告
        @param file_name: foo.png or fool
        @return:
        """
        # 把文件名处理成test.png的样式
        if '.' in file_name:
            file_name = file_name.split(r'.')[0]
        # 截图并保存到当前目录的images文件夹中
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%Y%m%d%H%M%S')
        file_path = os.path.join(img_dir,
                                 f'{file_name}-{time_str}.png')
        logger.info(f'截图保存至: {file_path}')
        self.d.save_screenshot(file_path)
        # 截图并上传到allure报告
        logger.info(f'截图上传至allure报告')
        allure.attach.file(file_path,
                           attachment_type=allure.attachment_type.PNG,
                           name=f'{file_name}-{time_str}')

    # @relaunch
    # def upload_pic(self, filename):
    #     # allure.attach.file(self.d.get_screenshot_as_png(),
    #     #                    attachment_type=allure.attachment_type.PNG,
    #     #                    name=f'{filename}')
    #     self.d.save_screenshot('tmp.png')
    #     allure.attach.file('tmp.png', attachment_type=allure.attachment_type.PNG,
    #                        name=f'{filename}-{get_time()}')
    #     os.remove('tmp.png')

    @property
    def page_content(self):
        page_source = self.d.page_source
        logger.info(f'获取页面内容: \n{page_source}')
        return page_source

    @relaunch
    def max_window(self):
        logger.info('窗口设置全屏')
        self.d.maximize_window()

    @relaunch
    def set_window_size(self, width, height):
        logger.info('设置窗口长宽')
        self.d.set_window_size(width, height)

    def get_windows(self):
        logger.info(f'获取当前打开的窗口列表')
        return self.d.window_handles

    @relaunch
    def switch_window(self, old_windows):
        logger.info('切换到最新的window')
        current_windows = self.d.window_handles
        newest_window = [window for window in current_windows if window not in old_windows][0]
        self.d.switch_to.window(newest_window)

    @relaunch
    def window_scroll(self, width, height):
        logger.info(f'设置scroll bar的宽高')
        js = "window.scrollTo({w},{h});".format(w=str(width), h=str(height))
        self.d.execute_script(js)

    @relaunch
    def switch_to_frame(self, frame_id):
        logger.info(f'切换到frame {frame_id}')
        self.d.switch_to.frame(frame_id)

    @relaunch
    def switch_to_frame_out(self):
        logger.info('从frame中切出来')
        self.d.switch_to.default_content()

    @relaunch
    def execute_js(self, script, *args):
        logger.info(f'执行js脚本: \n{script}')
        self.d.execute_script(script, *args)

    @relaunch
    def click(self, element):
        logger.info(f'点击元素: {element}')
        self.d.execute_script('arguments[0].click();', element)

    @relaunch
    def quit(self):
        logger.info('退出浏览器')
        self.d.quit()

    @relaunch
    def close(self):
        logger.info('关闭当前页签')
        self.d.close()

    @relaunch
    def add_cookies(self, cookies: list):
        for cookie in cookies:
            self.d.add_cookie(cookie)

    def get_cookies(self):
        logger.info('获取cookies')
        cookies = self.d.get_cookies()
        logger.info(cookies)
        return cookies

    def get_cookie(self, name):
        logger.info(f'获取cookie: {name}')
        cookie = self.d.get_cookie(name)
        logger.info(cookie)
        return cookie

    @relaunch
    def delete_all_cookies(self):
        logger.info('删除所有cookie')
        self.d.delete_all_cookies()

    @relaunch
    def delete_cookie(self, name):
        logger.info(f'删除cookie: {name}')
        self.d.delete_cookie(name)

    @relaunch
    def refresh(self):
        logger.info(f'刷新当前页')
        self.d.refresh()

    def get_title(self):
        logger.info('获取页面标题')
        title = self.d.title
        logger.info(title)
        return title

    def get_url(self):
        logger.info('获取页面url')
        url = self.d.current_url
        logger.info(url)
        return url

    def get_alert_text(self):
        logger.info('获取alert的文本')
        alert_text = self.d.switch_to.alert.text
        logger.info(alert_text)
        return alert_text

    @relaunch
    def accept_alert(self):
        logger.info('同意确认框')
        self.d.switch_to.alert.accept()

    @relaunch
    def dismiss_alert(self):
        logger.info('取消确认框')
        self.d.switch_to.alert.dismiss()





