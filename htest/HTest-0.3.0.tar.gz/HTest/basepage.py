#!/usr/bin/env python3.7
# encoding: utf-8
# 二次封装常用函数库
import os
import time
from random import choice
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from HTest.logger import logger


class BasePage(object):
    """
    定义一个页面基类，让所有页面都继承这个类，封装一些常用的页面操作方法到这个类

    """

    def __init__(self, driver):
        self.driver = driver

    def setup(self):
        pass

    def teardown(self):
        pass

    @property
    def get_title(self):
        """
        获取当前页面  title
        :return:
        """
        title = self.driver.title
        logger.debug(f"get current title {title}")
        return title

    @property
    def get_url(self):
        """
        获取当前页面的URL
        :return:
        """
        currentURL = self.driver.current_url
        logger.debug(f"get current url {currentURL}")
        return currentURL

    @property
    def get_url_html(self):
        """
        获取当前页面 html内容
        :return:
        """
        sourceHtml = self.driver.page_source
        return sourceHtml

    def refresh(self):
        """
        刷新当前页面
        :return:
        """
        logger.debug('refresh current page')
        return self.driver.refresh()

    def forward(self):
        """
        浏览器前进操作
        :return:
        """
        logger.info("Click forward on current content.")
        return self.driver.forward()

    def back(self):
        """
        浏览器后退操作
        :return:
        """
        logger.info("Click back on current content.")
        return self.driver.back()

    def wait(self, seconds):
        """
        隐式等待
        :param seconds:
        :return:
        """
        self.driver.implicitly_wait(seconds)
        logger.info("wait for %d seconds." % seconds)

    def visit(self, url):
        """
        打开窗口
        :param url:
        :return:
        """
        self.driver.get(url)

    def close(self):
        """
        关闭当前窗口
        :return:
        """
        try:
            self.driver.close()
            logger.info("Closing and quit the browser.")
        except NameError as e:
            logger.error("Failed to quit the browser with %s" % e)

    def quit(self):
        """
        关闭浏览器
        :return:
        """
        self.driver.quit()
        logger.info('quit the browser')

    def web_scroll_to_element(self, *selector):
        """
        滚动至元素element可见位置
        :return:
        """
        target = self.find_element(*selector)
        self.driver.execute_script("arguments[0].scrollIntoView();", target)

    # 查找元素
    def find_element(self, *selector):
        """
        多个元素定位
        :param selector: 传入元素属性
        :return: 定位到的元素
        """
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located(selector))
            return self.driver.find_element(*selector)
        except AttributeError:
            logger.error("{0}页面中未能找到{1}元素".format(self, selector))

    def input(self, text, *selector):
        """
        输入字符
        :param selector:
        :param text:
        :return:
        """
        el = self.find_element(*selector)
        try:
            el.clear()
            el.send_keys(text)
            logger.info("Had type \' %s \' in inputBox" % text)
        except NameError as e:
            logger.error("Failed to type in input box with %s" % e)

    def clear(self, *selector):
        """
        清除文本框
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        try:
            element.clear()
            logger.info("Clear text in input box before typing.")
        except NameError as e:
            logger.error("Failed to clear in input box with %s" % e)
            self.take_screenshot()

    @staticmethod
    def sleep(seconds):
        """
        加了@staticmethod,把外部方法集成到类体
        :param seconds:
        :return:
        """
        time.sleep(seconds)
        logger.info("Sleep for %d seconds" % seconds)

    def click(self, *selector):
        """
        点击
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        text = element.get_attribute('innerText')
        if text:
            text_name = text
        else:
            text_name = element.get_attribute('value')
        try:
            element.click()
            logger.info("The element \' %s \' was clicked." % text_name)
        except NameError as e:
            logger.error("Failed to click the element with %s" % e)

    def left_click(self, *selector):
        """
        模拟鼠标左击
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        try:
            ActionChains(self.driver).click(element).perform()
            logger.info("The element \' %s \' was clicked." % element.text)
        except NameError as e:
            logger.error("Failed to left_click the element with %s" % e)
            self.take_screenshot()

    def right_click(self, *selector):
        """
        模拟鼠标右击
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        try:
            ActionChains(self.driver).click(element).perform()
            logger.info("The element \' %s \' was clicked." % element.text)
        except NameError as e:
            logger.error("Failed to right_click the element with %s" % e)
            self.take_screenshot()

    def double_click(self, *selector):
        """
        双击
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        try:
            ActionChains(self.driver).double_click(element).perform()
        except Exception as e:
            logger.error("Failed to double_click the element with %s" % e)
            self.take_screenshot()
            raise

    def switch_iframe(self, *selector):
        """
        切到iframe
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        # noinspection PyBroadException
        try:
            self.driver.switch_to.frame(element)
            logger.info('Successful to switch_to_frame! ')
        except BaseException:
            logger.error('Failed to switch_to_frame!')

    def switch_menu(self, parent_element, sec_element, target_element):
        """
        三级菜单切换
        :param parent_element:
        :param sec_element:
        :param target_element:
        :return:
        """
        self.sleep(3)
        # noinspection PyBroadException
        try:
            self.driver.switch_to_default_content()
            self.click(parent_element)
            logger.info('成功点击一级菜单：%s' % parent_element)
            self.click(sec_element)
            logger.info('成功点击二级菜单：%s' % sec_element)
            self.click(target_element)
            logger.info('成功点击三级菜单：%s' % target_element)
        except BaseException:
            logger.error('切换菜单报错')

    def switch_windows(self, loc):
        """
        多窗口切换
        :param loc:
        :return:
        """
        try:
            return self.driver.switch_to_window(loc)
        except BaseException as msg:
            logger.error("查找窗口句柄handle异常-> {0}".format(msg))

    def switch_alert(self):
        """
        警告框处理
        :return:
        """
        try:
            return self.driver.switch_to_alert()
        except BaseException as msg:
            logger.error("查找alert弹出框异常-> {0}".format(msg))

    def quit_iframe(self):
        """
        退出当前iframe
        :return:
        """
        self.driver.switch_to_default_content()

    def get_select_count(self, selector):
        """
        获取下拉选项的个数
        :param selector:
        :return:
        """
        element = self.find_element(*selector)
        sel = Select(element)
        options = sel.options
        return options

    def select(self, id1):
        """
        处理标准下拉选择框,随机选择
        :param id1:
        :return:
        """
        select1 = self.find_element(*id1)
        try:
            options_list = select1.find_elements_by_tag_name('option')
            del options_list[0]
            s1 = choice(options_list)
            Select(select1).select_by_visible_text(s1.text)
            logger.info("随机选的是：%s" % s1.text)
        except NameError as e:
            logger.error("Failed to click the element with %s" % e)

    def execute_js(self, js):
        """
        执行js
        :param js:
        :return:
        """
        self.driver.execute_script(js)

    def enter(self, selector):
        """
        模拟回车键
        :param selector:
        :return:
        """
        e1 = self.find_element(*selector)
        e1.send_keys(Keys.ENTER)

    def up(self, selector):
        """
        模拟向上键
        :param selector:
        :return:
        """
        e1 = self.find_element(*selector)
        e1.send_keys(Keys.UP)

    def down(self, selector):
        """
        模拟向下键
        :param selector:
        :return:
        """
        e1 = self.find_element(*selector)
        e1.send_keys(Keys.DOWN)

    def take_screenshot(self):
        """
        截图，保存在根目录下的content/screenshots
        :return:
        """
        screen_dir = os.path.dirname(os.path.abspath('./content')) + '/screenshots/'
        rq = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        screen_name = screen_dir + rq + '.png'
        try:
            self.driver.get_screenshot_as_file(screen_name)
            logger.info("Had take screenshot and saved!")
        except Exception as e:
            logger.error("Failed to take screenshot with %s" % e)

    def is_displayed(self, xpath):
        """
        元素是否存在
        :param xpath:
        :return:
        """
        flag = True
        driver = self.driver
        try:
            driver.find_element_by_xpath(xpath)
            return flag
        except Exception as e:
            logger.info("Failed to displayed  with %s" % e)
            flag = False
            return flag

    def get_attribute(self, selector, attribute):
        """
        获取元素属性
        :param selector:
        :param attribute:
        :return:
        """
        try:
            element = self.find_element(*selector)
            return element.get_attribute(attribute)
        except Exception as e:
            logger.info("Failed to get_attribute  with %s" % e)
            self.take_screenshot()
            raise

    def get_text(self, selector):
        """
        获取元素的文本信息
        :param selector:
        :return:
        """
        try:
            return self.find_element(*selector).text
        except Exception as e:
            logger.info("Failed to get_text  with %s" % e)
            self.take_screenshot()

    def get_xpath(self, xpath):
        """
        通过XPATH获取元素
        :param xpath:
        :return:
        """
        element = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath(xpath))
        # element = self.driver.find_element_by_xpath(xpath)
        self.wait(1)
        return element

    def get_id(self, id2):
        """
        通过ID获取元素
        :param id2:
        :return:
        """
        element = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath(id2))
        # element = self.driver.find_element_by_id(id)
        self.wait(1)
        return element

    def get_name(self, name):
        """
        通过NAME获取元素
        :param name:
        :return:
        """
        element = WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath(name))
        # element = self.driver.find_element_by_name(name)
        self.wait(1)
        return element
