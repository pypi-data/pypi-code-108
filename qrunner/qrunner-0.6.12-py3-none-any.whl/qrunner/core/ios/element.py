import inspect
from typing import Union
from wda import Selector
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.ios.driver import relaunch_wda, IosDriver
from qrunner.utils.exceptions import ElementTypeError
from multiprocessing.dummy import Pool as ThreadPool
from selenium.common.exceptions import NoSuchElementException


# 默认支持的弹窗处理
IOS_ALERTS = [
    '使用App时允许',
    '允许',
    '始终允许'
]


class IosElement(object):
    """
    IOS原生元素定义
    """
    def __init__(self, *args, **kwargs):
        # 从kwargs中删掉并返回index
        self._index = kwargs.pop('index', 0)
        # 参数初始化
        self._pkg_name = conf.get_name('app', 'pkg_name')
        self._resourceId = kwargs.pop('resourceId', '')
        if self._resourceId:
            kwargs['resourceId'] = f'{self._pkg_name}:{self._resourceId}'
        self._xpath = kwargs.get('xpath', '')
        self._kwargs = kwargs
        self._element: Union[Selector] = None
        self._serial_no = conf.get_name('app', 'serial_no')
        self._driver = IosDriver.get_instance(self._serial_no)
        self._d = self._driver.d

    # 多线程处理异常弹窗
    def handle_alert(self):
        """
        根据不同定位方式进行点击
        @return:
        """
        def click_alert(loc):
            timeout = 2
            try:
                if '//' in loc:
                    self._d.xpath(loc).click(timeout=timeout)
                else:
                    self._d(name=loc).click(timeout=timeout)
            except Exception:
                pass

        # 弹窗列表设置
        alert_list = []
        alert_list.extend(IOS_ALERTS)  # 添加上面定义的默认支持弹窗列表
        user_set_list = conf.get_name('app', 'alerts').split(',')
        alert_list.extend(user_set_list)  # 添加用例在running/conf.ini中设置的弹窗列表

        # 多线程执行点击过程
        pool = ThreadPool(10)
        pool.map(click_alert, alert_list)

    @relaunch_wda
    def _find_element(self, retry=3, timeout=3):
        """
        循环查找元素，查找失败先处理弹窗后重试
        @param retry: 重试次数
        @param timeout: 单次查找超时时间
        @return:
        """
        self._element = self._d.xpath(self._xpath) if \
            self._xpath else self._d(**self._kwargs)[self._index]
        while not self._element.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.warning(f'重试 查找元素： {self._kwargs}')
                self.handle_alert()
            else:
                frame = inspect.currentframe().f_back
                caller = inspect.getframeinfo(frame)
                logger.warning(f'【{caller.function}:{caller.lineno}】未找到元素 {self._kwargs}')
                return None
        return self._element

    def get_element(self, retry=3, timeout=3):
        """
        针对元素定位失败的情况，抛出NoSuchElementException异常
        @param retry:
        @param timeout:
        @return:
        """
        element: Union[Selector] = self._find_element(retry=retry, timeout=timeout)
        if element is None:
            self._driver.screenshot(f'元素定位失败')
            raise NoSuchElementException(f'元素: {self._kwargs} 定位失败')
        return element

    @property
    def info(self):
        logger.info(f'获取元素: {self._kwargs} 的所有属性')
        return self.get_element().info

    @property
    def text(self):
        logger.info(f'获取元素: {self._kwargs} 的text属性')
        return self.get_element().text

    @property
    def className(self):
        logger.info(f'获取元素: {self._kwargs} 的className属性')
        return self.get_element().className

    @property
    def name(self):
        logger.info(f'获取元素: {self._kwargs} 的name属性')
        return self.get_element().name

    @property
    def visible(self):
        logger.info(f'获取元素: {self._kwargs} 的visible属性')
        return self.get_element().visible

    @property
    def value(self):
        logger.info(f'获取元素: {self._kwargs} 的value属性')
        return self.get_element().value

    @property
    def label(self):
        logger.info(f'获取元素: {self._kwargs} 的label属性')
        return self.get_element().label

    @property
    def enabled(self):
        logger.info(f'获取元素: {self._kwargs} 的enabled属性')
        return self.get_element().enabled

    @property
    def displayed(self):
        logger.info(f'获取元素: {self._kwargs} 的displayed属性')
        return self.get_element().displayed

    @property
    def bounds(self):
        logger.info(f'获取元素: {self._kwargs} 的bounds属性')
        return self.get_element().bounds

    def exists(self, timeout=1):
        """
        判断元素是否存在当前页面
        @param timeout:
        @return:
        """
        logger.info(f'元素 {self._kwargs},{self._index} 是否存在:')
        element = self._find_element(retry=0, timeout=timeout)
        if element is None:
            self._driver.screenshot(f'元素定位失败')
            return False
        return True

    def wait_gone(self, timeout=10):
        logger.info(f'等待元素{self._kwargs}消失')
        flag = self.get_element().wait_gone(timeout=timeout)
        logger.info(flag)
        return flag

    @relaunch_wda
    def click(self):
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        self.get_element().click()

    @relaunch_wda
    def click_exists(self):
        if self.exists():
            self.click()

    @relaunch_wda
    def clear_text(self):
        logger.info('清除文本: {text}')
        self.get_element().clear_text()

    @relaunch_wda
    def set_text(self, text):
        logger.info(f'输入框 {self._kwargs},{self._index} 输入: {text}')
        self.get_element().set_text(text)

    @relaunch_wda
    def scroll(self, direction=None):
        """
        scroll to make element visiable
        @param: direction，方向，"up", "down", "left", "right"
        @return:
        """
        if direction is not None:
            self.get_element().scroll(direction=direction)
        else:
            self.get_element().scroll()

    @relaunch_wda
    def swipe_left(self):
        self.get_element().swipe("left")

    @relaunch_wda
    def swipe_right(self):
        self.get_element().swipe("right")

    @relaunch_wda
    def swipe_up(self):
        self.get_element().swipe("up")

    @relaunch_wda
    def swipe_down(self):
        self.get_element().swipe("down")

    def child(self, *args, **kwargs):
        return self.get_element().child(*args, **kwargs)






