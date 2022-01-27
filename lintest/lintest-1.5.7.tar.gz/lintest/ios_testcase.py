from .base_testcase import BaseTestCase


class IOSTestCase(BaseTestCase):
    """
    IOSTestCase is the base class for all the IOS Test cases

    @author: Lin.Wang
    """

    def __init__(self):
        from appium import webdriver
        self.ios_driver = webdriver.Remote
