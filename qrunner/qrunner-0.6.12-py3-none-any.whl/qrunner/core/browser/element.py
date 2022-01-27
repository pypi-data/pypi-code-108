import inspect
import os
import time
import platform

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement as WE
from qrunner.utils.log import logger
from qrunner.core.browser.driver import relaunch
from qrunner.utils.exceptions import ElementTypeError, NoSuchElementException
from qrunner.core.browser.driver import BrowserDriver


# 支持的定位方式
LOC_LIST = {
    'id_': By.ID,
    'name': By.NAME,
    'linkText': By.LINK_TEXT,
    'tagName': By.TAG_NAME,
    'partialLinkText': By.PARTIAL_LINK_TEXT,
    'className': By.CLASS_NAME,
    'xpath': By.XPATH,
    'css': By.CSS_SELECTOR
}


class WebElement:
    """
    Web元素定义
    """
    def __init__(self, driver, **kwargs):
        self._index = kwargs.pop('index', 0)

        if not kwargs:
            raise ElementTypeError('请输入定位方式')

        if len(kwargs) > 1:
            raise ElementTypeError('请仅指定一种定位方式')

        self.k, self.v = next(iter(kwargs.items()))
        # print(self.k, self.v)
        if self.k not in LOC_LIST.keys():
            raise ElementTypeError(f'不支持的定位方式: {self.k}，仅支持: {LOC_LIST.keys()}')

        self._kwargs = kwargs
        self._element = None
        self.driver: BrowserDriver = driver
        self.d = self.driver.d

    @relaunch
    def _wait(self, timeout=3):
        try:
            WebDriverWait(self.d, timeout=timeout)\
                .until(EC.visibility_of_element_located((LOC_LIST[self.k], self.v)))
            return True
        except Exception:
            return False

    @relaunch
    def _find_element(self, retry=3, timeout=5):
        while not self._wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.info(f'重试 查找元素 {self._kwargs}')
                time.sleep(2)
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】Not found element {self._kwargs}')
                return None
        elements = self.d.find_elements(LOC_LIST[self.k], self.v)
        return elements

    @relaunch
    def show_element(self, elem):
        """
                Show the elements of the operation
                :param elem:
                """
        style_red = 'arguments[0].style.border="2px solid #FF0000"'
        style_blue = 'arguments[0].style.border="2px solid #00FF00"'
        style_null = 'arguments[0].style.border=""'
        for _ in range(2):
            self.driver.execute_js(style_red, elem)
            time.sleep(0.1)
            self.driver.execute_js(style_blue, elem)
            time.sleep(0.1)
        self.driver.execute_js(style_blue, elem)
        time.sleep(0.3)
        self.driver.execute_js(style_null, elem)

    def get_elements(self, retry=3, timeout=3):
        elements = self._find_element(retry=retry, timeout=timeout)
        if elements is None:
            self.driver.screenshot('元素定位失败')
            raise NoSuchElementException(f'{self._kwargs}-定位失败')
        return elements

    def get_element(self, retry=3, timeout=3):
        elements = self._find_element(retry=retry, timeout=timeout)
        if elements is None:
            self.driver.screenshot('元素定位失败')
            raise NoSuchElementException(f'{self._kwargs}-定位失败')
        else:
            element: WE = elements[self._index]
            self.show_element(element)
        return element

    def exists(self, timeout=1):
        logger.info(f'判断元素: {self._kwargs} 是否存在')
        element = self._find_element(retry=0, timeout=timeout)
        if element is None:
            self.driver.screenshot(f'元素定位失败')
            return False
        return True

    @relaunch
    def click(self):
        logger.info(f'点击元素: {self._kwargs}')
        self.get_element().click()

    @relaunch
    def slow_click(self):
        logger.info(f'移动到元素{self._kwargs}，然后点击')
        elem = self.get_element()
        ActionChains(self.d).move_to_element(elem).click(elem).perform()

    @relaunch
    def right_click(self):
        logger.info(f'右键元素{self._kwargs}')
        elem = self.get_element()
        ActionChains(self.d).context_click(elem).perform()

    @relaunch
    def move_to_elem(self):
        logger.info(f'鼠标移动到元素{self._kwargs}上')
        elem = self.get_element()
        ActionChains(self.d).move_to_element(elem).perform()

    @relaunch
    def click_and_hold(self):
        logger.info(f'长按元素: {self._kwargs}')
        elem = self.get_element()
        ActionChains(self.d).click_and_hold(elem).perform()

    @relaunch
    def drag_and_drop(self, x, y):
        logger.info(f'拖动元素{self._kwargs}到坐标{x},{y}')
        elem = self.get_element()
        action = ActionChains(self.d)
        action.drag_and_drop_by_offset(elem, x, y).perform()

    @relaunch
    def double_click(self):
        logger.info(f'双击元素: {self._kwargs}')
        elem = self.get_element()
        ActionChains(self.d).double_click(elem).perform()

    @relaunch
    def send_keys(self, text):
        logger.info(f'点击元素: {self._kwargs}，然后输入: {text}')
        self.get_element().send_keys(text)

    @relaunch
    def clear_text(self):
        logger.info(f'清空文本')
        self.get_element().clear()

    @relaunch
    def enter(self):
        logger.info(f'选中元素{self._kwargs}点击enter')
        self.get_element().send_keys(Keys.ENTER)

    @relaunch
    def select_all(self) -> None:
        logger.info(f"选中元素{self._kwargs}, ctrl+a.")
        if platform.system().lower() == "darwin":
            self.get_element().send_keys(Keys.COMMAND, "a")
        else:
            self.get_element().send_keys(Keys.CONTROL, "a")

    @relaunch
    def cut(self) -> None:
        logger.info(f"选中元素{self._kwargs}, ctrl+x.")
        if platform.system().lower() == "darwin":
            self.get_element().send_keys(Keys.COMMAND, "x")
        else:
            self.get_element().send_keys(Keys.CONTROL, "x")

    @relaunch
    def copy(self) -> None:
        logger.info(f"选中元素{self._kwargs}, ctrl+c.")
        if platform.system().lower() == "darwin":
            self.get_element().send_keys(Keys.COMMAND, "c")
        else:
            self.get_element().send_keys(Keys.CONTROL, "c")

    @relaunch
    def paste(self) -> None:
        logger.info(f"选中元素{self._kwargs}, ctrl+v.")
        if platform.system().lower() == "darwin":
            self.get_element().send_keys(Keys.COMMAND, "v")
        else:
            self.get_element().send_keys(Keys.CONTROL, "v")

    @relaunch
    def backspace(self) -> None:
        logger.info(f"选中元素{self._kwargs}, backspace.")
        self.get_element().send_keys(Keys.BACKSPACE)

    @relaunch
    def delete(self) -> None:
        logger.info(f"选中元素{self._kwargs}, delete.")
        self.get_element().send_keys(Keys.DELETE)

    @relaunch
    def tab(self) -> None:
        logger.info(f"选中元素{self._kwargs}, tab.")
        self.get_element().send_keys(Keys.TAB)

    @relaunch
    def space(self) -> None:
        logger.info(f"选中元素{self._kwargs}, space.")
        self.get_element().send_keys(Keys.SPACE)

    def get_attr(self, attr_name):
        logger.info(f'获取属性{attr_name}的值')
        value = self.get_element().get_attribute(attr_name)
        logger.info(value)
        return value

    def get_display(self):
        logger.info(f'获取元素{self._kwargs}的display属性')
        displayed = self.get_element().is_displayed()
        logger.info(displayed)
        return displayed

    def get_text(self):
        logger.info(f'获取元素 {self._kwargs} 文本')
        element = self.get_element()
        text = element.text
        logger.info(text)
        return text

    def get_texts(self):
        logger.info(f'获取元素 {self._kwargs} 文本列表')
        elements = self.get_elements()
        texts = [elem.text for elem in elements]
        logger.info(texts)
        return texts

    @relaunch
    def select_index(self, index):
        logger.info(f'选择第 {index} 个下拉列表')
        element = self.get_element()
        select = Select(element)
        select.select_by_index(index)

    @relaunch
    def select_value(self, value):
        logger.info(f'选择id为 {value} 的下拉列表')
        element = self.get_element()
        select = Select(element)
        select.select_by_value(value)

    @relaunch
    def select_text(self, text):
        logger.info(f'选择下拉列表 {text} 选项')
        element = self.get_element()
        select = Select(element)
        select.select_by_value(text)

    @relaunch
    def submit(self):
        logger.info(f'提交表单: {self._kwargs}')
        elem = self.get_element()
        elem.submit()

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
        self.get_element().screenshot(file_path)
        # 截图并上传到allure报告
        logger.info(f'截图上传至allure报告')
        allure.attach.file(file_path,
                           attachment_type=allure.attachment_type.PNG,
                           name=f'{file_name}-{time_str}')


