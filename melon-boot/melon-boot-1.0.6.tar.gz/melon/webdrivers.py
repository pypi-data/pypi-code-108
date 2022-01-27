# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
from selenium import webdriver
from melon.settings import get_config


def create_driver():
    driver_map = dict(CHROME=webdriver.Chrome, FIREFOX=webdriver.Firefox, IE=webdriver.Ie, EDGE=webdriver.Edge)

    url = get_config('melon.selenium.url')
    assert url and url != '', 'URL不能为空'

    browser_type = get_config('melon.selenium.browser', 'CHROME')
    func = driver_map.get(browser_type.upper())
    assert func, f'不支持的浏览器: [{browser_type}]'

    _driver = func()

    _driver.get(url)
    _driver.implicitly_wait(get_config('melon.selenium.implicitly_wait', 0))
    if get_config('melon.selenium.maximize_window', False):
        _driver.maximize_window()
    return _driver


driver = create_driver()

