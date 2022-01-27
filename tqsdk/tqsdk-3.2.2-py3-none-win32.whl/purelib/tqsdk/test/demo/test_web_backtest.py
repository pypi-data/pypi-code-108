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
import unittest
from datetime import date

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from tqsdk import TqApi, TqBacktest, TargetPosTask
from tqsdk.exceptions import BacktestFinished
# 子进程要执行的代码
from tqsdk.test.helper import MockInsServer


def run_tianqin_code(port, queue, ins_port):
    try:
        os.environ["TQ_INS_URL"] = f"http://127.0.0.1:{ins_port}/t/md/symbols/2020-09-15.json"
        os.environ["TQ_AUTH_URL"] = f"http://127.0.0.1:{ins_port}"
        api = TqApi(backtest=TqBacktest(start_dt=date(2020, 7, 10), end_dt=date(2020, 7, 20)), auth="tianqin,tianqin",
                    web_gui="127.0.0.1:" + port, _md_url="wss://nfmd.shinnytech.com/t/nfmd/front/mobile")
        queue.put("webready")
        klines = api.get_kline_serial("DCE.m2009", 5 * 60, data_length=15)
        target_pos = TargetPosTask(api, "DCE.m2009")
        while True:
            api.wait_update()
            if api.is_changing(klines):
                ma = sum(klines.close.iloc[-15:]) / 15
                if klines.close.iloc[-1] > ma:
                    target_pos.set_target_volume(5)
                elif klines.close.iloc[-1] < ma:
                    target_pos.set_target_volume(0)
    except BacktestFinished as e:
        while True:
            api.wait_update()
    except Exception as e:
        api.close()

@pytest.mark.skip(reason="temporarily remove")
@pytest.mark.flaky(reruns=6)
@pytest.mark.nonparalleltest
class WebTestOnChrome(unittest.TestCase):

    def setUp(self) -> None:
        self.ins = MockInsServer()
        self.chrome_options = ChromeOptions()
        self.chrome_options.headless = True
        ctx = mp.get_context('spawn')
        self.port = "8082"
        self.q = ctx.Queue()
        self.tq_process = ctx.Process(target=run_tianqin_code, args=(self.port, self.q, self.ins.port))
        self.tq_process.start()
        self.q.get()

    def tearDown(self):
        self.ins.close()
        self.tq_process.terminate()

    @unittest.skipIf(not sys.platform.startswith("win"), "test on win")
    def test_on_win(self):
        chromedriver_path = os.path.join(os.getenv("ChromeWebDriver"), "chromedriver.exe")
        run_for_driver(webdriver.Chrome(executable_path=chromedriver_path, options=self.chrome_options), self)

    @unittest.skipIf(not sys.platform.startswith("linux"), "test on linux")
    def test_on_linux(self):
        exe_path = os.path.join(os.getenv("CHROMEWEBDRIVER"), "chromedriver")
        driver = webdriver.Chrome(executable_path=exe_path, options=self.chrome_options)
        run_for_driver(driver, self)

    @unittest.skipIf(not sys.platform.startswith("darwin"), "test on macos")
    def test_on_macos(self):
        run_for_driver(webdriver.Chrome(options=self.chrome_options), self)

@pytest.mark.skip(reason="temporarily remove")
@pytest.mark.flaky(reruns=6)
@pytest.mark.nonparalleltest
class WebTestOnFirefox(unittest.TestCase):

    def setUp(self) -> None:
        self.ins = MockInsServer(5000)
        self.ins_url_2020_06_27 = "http://127.0.0.1:5000/t/md/symbols/2020-06-27.json"
        self.firefox_options = FirefoxOptions()
        self.firefox_options.headless = True
        ctx = mp.get_context('spawn')
        self.port = "8081"
        self.q = ctx.Queue()
        self.tq_process = ctx.Process(target=run_tianqin_code, args=(self.port, self.q))
        self.tq_process.start()
        self.q.get()

    def tearDown(self):
        self.ins.close()
        self.tq_process.terminate()

    @unittest.skipIf(not sys.platform.startswith("win"), "test on win")
    def test_on_win(self):
        geckodriver_path = os.path.join(os.getenv("GeckoWebDriver"), "geckodriver.exe")
        run_for_driver(webdriver.Firefox(executable_path=geckodriver_path, options=self.firefox_options), self)

    @unittest.skipIf(not sys.platform.startswith("linux"), "test on linux")
    def test_on_linux(self):
        exe_path = os.path.join(os.getenv("GECKOWEBDRIVER"), "geckodriver")
        driver = webdriver.Firefox(executable_path=exe_path, options=self.firefox_options)
        run_for_driver(driver, self)

    @unittest.skipIf(not sys.platform.startswith("darwin"), "test on macos")
    def test_on_macos(self):
        run_for_driver(webdriver.Firefox(options=self.firefox_options), self)


def run_for_driver(driver, test):
    driver.implicitly_wait(30)
    driver.get("http://127.0.0.1:" + test.port)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.title_is("tqsdk-python-web"))  # k线图显示
    logo = driver.find_element_by_tag_name("img")
    test.assertEqual("Tianqin", logo.get_attribute("alt"))
    # K线是否有成交箭头
    chart_main_marks = driver.find_element_by_css_selector("svg.tqchart>g.root g.main.marks")
    trade_arrow_paths = chart_main_marks.find_element_by_css_selector("g.tradearrow")
    wait.until(element_has_child(trade_arrow_paths, "path"))
    # 成交列表是否显示
    trades_table = driver.find_element_by_css_selector("div.reports.trades-table>table")
    wait.until(element_has_child(trades_table, "tbody>tr"))
    driver.close()


class element_has_child(object):
    def __init__(self, element, css_selector):
        self.element = element
        self.css_selector = css_selector

    def __call__(self, driver):
        children = self.element.find_element_by_css_selector(self.css_selector)
        if not children:
            return False
        return True


if __name__ == "__main__":
    unittest.main()
