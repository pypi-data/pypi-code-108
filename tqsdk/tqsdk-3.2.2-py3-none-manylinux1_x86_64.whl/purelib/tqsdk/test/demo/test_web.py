#!usr/bin/env python3
#-*- coding:utf-8 -*-
"""
@author: yanqiong
@file: test_web.py
@create_on: 2020/2/12
@description: "Users/yanqiong/Documents/geckodriver-v0.26.0-macos.tar.gz"
"""
import multiprocessing as mp
import os
import sys
import time
import unittest

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tqsdk import TqApi
from tqsdk.ta import MA
from tqsdk.test.helper import MockInsServer


# 子进程要执行的代码


def run_tianqin_code(port, webtest_queue, api_queue, ins_port):
    os.environ["TQ_INS_URL"] = f"http://127.0.0.1:{ins_port}/t/md/symbols/2020-09-15.json"
    os.environ["TQ_AUTH_URL"] = f"http://127.0.0.1:{ins_port}"
    try:
        api = TqApi(auth="tianqin,tianqin", web_gui="127.0.0.1:" + port, _md_url="wss://api.shinnytech.com/t/nfmd/front/mobile")
        webtest_queue.put("web_ready")
        klines = api.get_kline_serial("KQ.m@SHFE.rb", 24 * 60 * 60)
        ma = MA(klines, 30)  # 使用tqsdk自带指标函数计算均线
        while True:
            deadline = time.time() + 2
            api.wait_update(deadline)
            if not api_queue.empty():
                api_queue.get()
                break
    finally:
        api.close()
        webtest_queue.put("web_closed")

@pytest.mark.flaky(reruns=6)
@pytest.mark.nonparalleltest
class WebTestOnChrome(unittest.TestCase):

    def setUp(self) -> None:
        self.ins = MockInsServer()
        self.chrome_options = ChromeOptions()
        self.chrome_options.headless = True
        ctx = mp.get_context('spawn')
        self.port = "8084"
        self.webtest_queue, self.api_queue = ctx.Queue(), ctx.Queue()
        self.tq_process = ctx.Process(target=run_tianqin_code, args=(self.port, self.webtest_queue, self.api_queue, self.ins.port))
        self.tq_process.start()
        r = self.webtest_queue.get()
        self.web_closed = True if r == "web_closed" else False

    def tearDown(self):
        if not self.web_closed:
            self.api_queue.put("web_should_close")
            self.webtest_queue.get()
        self.driver.close()
        self.ins.close()
        self.tq_process.terminate()

    @unittest.skipIf(not sys.platform.startswith("win"), "test on win")
    def test_on_win(self):
        chromedriver_path = os.path.join(os.getenv("ChromeWebDriver"), "chromedriver.exe")
        self.driver = webdriver.Chrome(executable_path=chromedriver_path, options=self.chrome_options)
        run_for_driver(self.driver, self)

    # @unittest.skipIf(not sys.platform.startswith("linux"), "test on linux")
    @unittest.skip("test on linux")
    def test_on_linux(self):
        exe_path = os.path.join(os.getenv("CHROMEWEBDRIVER"), "chromedriver")
        self.driver = webdriver.Chrome(executable_path=exe_path, options=self.chrome_options)
        run_for_driver(self.driver, self)

    @unittest.skipIf(not sys.platform.startswith("darwin"), "test on macos")
    def test_on_macos(self):
        self.driver = webdriver.Chrome(options=self.chrome_options)
        run_for_driver(self.driver, self)


@pytest.mark.skip(reason="temporarily remove")
@pytest.mark.flaky(reruns=6)
@pytest.mark.nonparalleltest
class WebTestOnFirefox(unittest.TestCase):

    def setUp(self) -> None:
        self.ins = MockInsServer()
        self.firefox_options = FirefoxOptions()
        self.firefox_options.headless = True
        ctx = mp.get_context('spawn')
        self.port = "8083"
        self.webtest_queue, self.api_queue = ctx.Queue(), ctx.Queue()
        self.tq_process = ctx.Process(target=run_tianqin_code, args=(self.port, self.webtest_queue, self.api_queue, self.ins.port))
        self.tq_process.start()
        r = self.webtest_queue.get()
        self.web_closed = True if r == "web_closed" else False

    def tearDown(self):
        if not self.web_closed:
            self.api_queue.put("web_should_close")
            self.webtest_queue.get()
        self.driver.close()
        self.ins.close()
        self.tq_process.terminate()

    @unittest.skipIf(not sys.platform.startswith("win"), "test on win")
    def test_on_win(self):
        geckodriver_path = os.path.join(os.getenv("GeckoWebDriver"), "geckodriver.exe")
        self.driver = webdriver.Firefox(executable_path=geckodriver_path, options=self.firefox_options)
        run_for_driver(self.driver, self)

    @unittest.skipIf(not sys.platform.startswith("linux"), "test on linux")
    def test_on_linux(self):
        exe_path = os.path.join(os.getenv("GECKOWEBDRIVER"), "geckodriver")
        self.driver = webdriver.Firefox(executable_path=exe_path, options=self.firefox_options)
        run_for_driver(self.driver, self)

    @unittest.skipIf(not sys.platform.startswith("darwin"), "test on macos")
    def test_on_macos(self):
        self.driver = webdriver.Firefox(options=self.firefox_options)
        run_for_driver(self.driver, self)


def run_for_driver(driver, test):
    driver.implicitly_wait(30)
    driver.get("http://127.0.0.1:" + test.port)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.title_is("tqsdk-python-web"))  # k线图显示
    logo = driver.find_element_by_tag_name("img")
    test.assertEqual("Tianqin", logo.get_attribute("alt"))
    account_info = driver.find_element_by_class_name("account-info")
    accounts = account_info.find_elements_by_tag_name("div")
    test.assertEqual(5, len(accounts))
    # 测试K线图是否显示
    chart_table = driver.find_element_by_css_selector("table.tqchart-table")

class path_element_has_d(object):
    """
    path  element 对象有内容
    """
    def __init__(self, element):
        self.element = element

    def __call__(self, driver):
        d = self.element.get_attribute("d")
        if not d:
            return False
        return d


if __name__ == "__main__":
    unittest.main()
