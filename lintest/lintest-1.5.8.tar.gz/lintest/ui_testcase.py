import traceback

from .base_testcase import BaseTestCase
from .selenium_helper import SeleniumHelper
from selenium.webdriver.remote.webdriver import WebDriver


class UITestCase(BaseTestCase):
    """
    UITestCase is the superclass for all the UI Test cases

    @author: Wang Lin
    """

    def __init__(self):
        super().__init__()
        self.browser = WebDriver

    def create_browser_driver(self):
        self.browser = SeleniumHelper.open_browser(self)

    def close_browser(self):
        browser_list = []

        for key, val in self.__dict__.items():
            if isinstance(val, WebDriver):
                browser_list.append(key)

        for browser in browser_list:
            webdriver = getattr(self, browser)
            try:
                webdriver.delete_all_cookies()
                webdriver.quit()
            except BaseException:
                traceback.print_exc()
