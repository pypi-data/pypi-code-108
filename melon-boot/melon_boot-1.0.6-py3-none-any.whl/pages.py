# -*- encoding: utf-8 -*-
"""
@Author  : zh_o
"""
from typing import Tuple, List, Text
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from melon.webdrivers import driver
from melon.settings import get_config


_LOCATOR_MAP = {
    'css': By.CSS_SELECTOR,
    'id_': By.ID,
    'xpath': By.XPATH,
    'name': By.NAME
}


class PageElement(WebElement):

    def __init__(self, label: Text, **kwargs):
        super().__init__('', '')
        self.label = label
        if not kwargs:
            raise ValueError('locator must not be null')
        if len(kwargs) > 1:
            raise ValueError('locator must be unique')
        key, val = next(iter(kwargs.items()))
        self.locator = (_LOCATOR_MAP[key], val)


class BasePage:

    def __init__(self):
        self.driver = driver
        self.element_dict = object.__getattribute__(self, '__dict__')

    def find_element(self, locator: Tuple) -> WebElement:
        _element = self.driver.find_element(*locator)
        original_click = _element.click
        original_send_keys = _element.send_keys

        def _click():
            with allure.step(f'点击{getattr(_element, "_label")}'):
                original_click()

        def _send_keys(*value):
            with allure.step(f'输入{getattr(_element, "_label")}: {" ".join(value)}'):
                original_send_keys(*value)

        _element.click = _click
        _element.send_keys = _send_keys
        return _element

    def find_elements(self, locator: Tuple) -> List[WebElement]:
        _elements = self.driver.find_elements(*locator)
        return _elements

    def switch_to_frame(self, frame_reference):
        self.driver.switch_to_frame(frame_reference)

    def switch_to_alert(self):
        self.driver.switch_to_alert()

    def action_chains(self) -> ActionChains:
        return ActionChains(self.driver)

    def open(self, url: Text):
        base_url = get_config('melon.selenium.url')

        if url.startswith('http://') or url.startswith('https://'):
            self.driver.get(url)
            return
        if not url.startswith('/'):
            url = '/' + url
        if base_url.endswith('/'):
            base_url = base_url[:-1]
        self.driver.get(f'{base_url}{url}')

    def close(self):
        self.__step('关闭浏览器', self.driver.close)

    def __step(self, description: Text, func):
        with allure.step(f'{self.__class__.__name__} => {description}'):
            return func()

    def __getattribute__(self, attr):
        # e_ 或 _e_ 开头属性需代理
        if attr.startswith('e_') or attr.startswith('_e_'):
            # 获取目标属性(被代理属性)
            _target = self.element_dict[attr]
            if not _target:
                return object.__getattribute__(self, attr)

            if isinstance(_target, (list, tuple)) or type(_target) == dict or type(_target) == tuple:
                # 可迭代属性
                _proxy = self.__proxy_iterable(_target)
            else:
                # 单属性
                _proxy = self.__proxy_single(_target)

            return _proxy

        return object.__getattribute__(self, attr)

    def __proxy_single(self, _target):
        """
        代理单属性
        """
        _proxy = self.find_element(_target.locator)
        _proxy._label = _target.label
        return _proxy

    def __proxy_iterable(self, _target):
        """
        代理可迭代属性
        """
        assert len(_target) > 0, 'melon elements must not be empty'
        _proxy = self.find_elements(_target[0].locator)
        [setattr(e, '_label', _target[0].label) for e in _proxy if e]
        return _proxy
