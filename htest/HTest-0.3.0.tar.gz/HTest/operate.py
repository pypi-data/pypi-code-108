#!/usr/bin/env python3.7
# _*_ coding:utf-8 _*_
import time
import unittest

from ddt import ddt, data, unpack
from selenium import webdriver
from selenium.webdriver.common.by import By
from HTest import BasePage, get_yaml
from HTest.logger import logger

data_suit = get_yaml().get("main-list")
data_case = get_yaml().get("case-list")
url = get_yaml().get("url")
print(url)
if data_suit is None or data_case is None or url is None:
    logger.error("Testcase file content is incorrect")
    exit(0)


@ddt
class yamlPage(unittest.TestCase):
    """
    value = value.split(',')[0].replace("'", "")
    修改用例名过长的问题
    在ddt.py中的mk_test_name方法中添加在倒数第三行
    order by tao
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.BasePage = BasePage(cls.driver)
        cls.driver.get(url)
        time.sleep(1)

    @data(*data_suit)
    @unpack
    def test_yml(self, *args):
        logger.debug("测试的用例是:{0}".format(args[0]))
        for i in range(1, len(data_case)):
            if data_case[i][0] == "hs-input":
                if data_case[i][1] == "id":
                    self.BasePage.input(args[i], By.ID, data_case[i][2])
                if data_case[i][1] == "name":
                    self.BasePage.input(args[i], By.NAME, data_case[i][2])
                if data_case[i][1] == "xpath":
                    self.BasePage.input(args[i], By.XPATH, data_case[i][2])
            if data_case[i][0] == 'hs-click':
                if data_case[i][1] == "id":
                    self.BasePage.click(By.ID, data_case[i][2])
                if data_case[i][1] == "name":
                    self.BasePage.click(By.NAME, data_case[i][2])
                if data_case[i][1] == "xpath":
                    self.BasePage.click(By.XPATH, data_case[i][2])
                time.sleep(3)
        logger.info("该条测试用例的执行结果是: " + args[-1])

    @classmethod
    def tearDownClass(cls) -> None:
        cls.driver.quit()


if __name__ == '__main__':
    unittest.main()
