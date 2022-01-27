import inspect
import os
import time
from multiprocessing.dummy import Pool as ThreadPool
from typing import Union
from uiautomator2 import UiObject
from uiautomator2.xpath import XPathSelector
from qrunner.utils.log import logger
from qrunner.utils.config import conf
from qrunner.core.android.driver import AndroidDriver
from qrunner.utils.exceptions import ElementTypeError, NoSuchElementException


# 默认支持的弹窗处理
ANDROID_ALERTS = [
    '允许',
    '始终允许',
    '仅使用期间允许',
    '仅在使用中允许'
]


class AndroidElement(object):
    """
    安卓元素定义
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
        self._element: Union[UiObject, XPathSelector] = None
        self._serial_no = conf.get_name('app', 'serial_no')
        self._driver = AndroidDriver.get_instance(self._serial_no)
        self._d = self._driver.d

    def handle_alert(self):
        """
        根据不同定位方式进行点击
        @return:
        """
        def click_alert(loc):
            timeout = 2
            try:
                if 'id/' in loc:
                    element = self._d(resourceId=f'{self._pkg_name}:{loc}')
                elif '//' in loc:
                    element = self._d.xpath(loc)
                else:
                    element = self._d(text=loc)
                element.click(timeout=timeout)
            except Exception:
                pass

        # 弹窗列表设置
        alert_list = []
        alert_list.extend(ANDROID_ALERTS)  # 添加上面定义的默认支持弹窗列表
        user_set_list = conf.get_name('app', 'alerts').split(',')
        alert_list.extend(user_set_list)  # 添加用例在running/conf.ini中设置的弹窗列表

        # 多线程执行点击过程
        pool = ThreadPool(10)
        pool.map(click_alert, alert_list)

    def _find_element(self, retry=3, timeout=3):
        """
        循环查找元素，查找失败先处理弹窗后重试，后面再考虑xpath要不要用.all()改造一下
        @param retry: 重试次数
        @param timeout: 每次查找超时时间
        @return: 找到的元素列表
        """
        logger.info(f'查找元素: {self._kwargs},{self._index}')
        self._element = self._d.xpath(self._xpath) if \
            self._xpath else self._d(**self._kwargs)[self._index]
        while not self._element.wait(timeout=timeout):
            if retry > 0:
                retry -= 1
                logger.warning(f'重试 查找元素： {self._kwargs},{self._index}')
                self.handle_alert()  # 处理异常弹窗
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
        element = self._find_element(retry=retry, timeout=timeout)
        if element is None:
            self._driver.screenshot(f'元素定位失败')
            raise NoSuchElementException(f'{self._kwargs}-定位失败')
        return element

    @property
    def info(self):
        logger.info(f'获取元素: {self._kwargs} 的所有信息')
        return self.get_element().info

    @property
    def text(self):
        logger.info(f'获取元素: {self._kwargs} 的文本')
        return self.get_element().info.get('text')

    @property
    def bounds(self):
        logger.info(f'获取元素: {self._kwargs} 的坐标')
        return self.get_element().info.get('bounds')

    @property
    def visibleBounds(self):
        logger.info(f'获取元素: {self._kwargs} 的可见坐标')
        return self.get_element().info.get('visibleBounds')

    @property
    def focusable(self):
        logger.info(f'获取元素: {self._kwargs} 是否聚焦')
        return self.get_element().info.get('focusable')

    @property
    def selected(self):
        logger.info(f'获取元素: {self._kwargs} 是否选中')
        return self.get_element().info.get('selected')

    def child(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的子元素{kwargs}')
        return self.get_element().child(*args, **kwargs)

    def brother(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs},{self._index} 的兄弟元素{kwargs}')
        return self.get_element().sibling(*args, **kwargs)

    def left(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 左边的元素 {kwargs}')
        return self.get_element().left(*args, **kwargs)

    def right(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 右边的元素 {kwargs}')
        return self.get_element().right(*args, **kwargs)

    def up(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 上边的元素 {kwargs}')
        return self.get_element().up(*args, **kwargs)

    def down(self, *args, **kwargs):
        logger.info(f'获取元素 {self._kwargs} 下边的元素 {kwargs}')
        return self.get_element().down(*args, **kwargs)

    def exists(self, timeout=1):
        logger.info(f'判断元素是否存在: {self._kwargs},{self._index}')
        element = self._find_element(retry=0, timeout=timeout)
        if element is None:
            self._driver.screenshot(f'元素定位失败')
            return False
        return True

    def click(self):
        logger.info(f'点击元素: {self._kwargs},{self._index}')
        self.get_element().click()

    def click_exists(self):
        logger.info(f'存在才点击元素: {self._kwargs},{self._index}')
        if self.exists():
            self.get_element().click()

    def click_gone(self):
        logger.info(f'等元素 {self._kwargs} 消失后再点击')
        flag = self.get_element().click_gone()
        logger.info(flag)
        return flag

    def wait_gone(self, timeout=3):
        logger.info(f'等元素 {self._kwargs} 消失')
        flag = self.get_element().wait_gone(timeout=timeout)
        logger.info(flag)
        return flag

    def long_click(self):
        logger.info(f'长按元素 {self._kwargs}')
        self.get_element().long_click()

    def set_text(self, text):
        logger.info(f'输入文本: {text}')
        self.get_element().set_text(text)

    def clear_text(self):
        logger.info('清除文本')
        self.get_element().clear_text()

    def drag_to(self, *args, **kwargs):
        logger.info(f'从当前元素{self._kwargs},{self._index}, 拖动到元素: {kwargs}')
        self.get_element().drag_to(*args, **kwargs)

    def swipe_left(self):
        logger.info(f'往左滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("left")

    def swipe_right(self):
        logger.info(f'往右滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("right")

    def swipe_up(self):
        logger.info(f'往上滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("up")

    def swipe_down(self):
        logger.info(f'往下滑动元素: {self._kwargs},{self._index}')
        self.get_element().swipe("down")

    def screenshot(self):
        logger.info(f'元素 {self._kwargs}截图')
        file_name = list(self._kwargs.values())[0]
        img_dir = os.path.join(os.getcwd(), 'images')
        if os.path.exists(img_dir) is False:
            os.mkdir(img_dir)
        time_str = time.strftime('%m%d%H%M%S')
        file_path = os.path.join(img_dir,
                                 f'{file_name}-{time_str}.png')
        logger.info(f'截图保存至: {file_path}')
        self.get_element().screenshot().save(file_path)


