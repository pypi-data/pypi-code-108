from .base_testcase import BaseTestCase


class AndroidTestCase(BaseTestCase):
    """
    AndroidTestCase is the base class for all the Android Test cases

    @author: WangLin
    """

    REAL_DEVICE = "_real_device_"
    VIRTUAL_DEVICE = "_virtual_device_"

    def __init__(self):
        self.username_temp = "USERNAME_TEMP"
        self.password_temp = "PASSWORD_TEMP"

        from appium import webdriver
        self.android_driver = webdriver.Remote
