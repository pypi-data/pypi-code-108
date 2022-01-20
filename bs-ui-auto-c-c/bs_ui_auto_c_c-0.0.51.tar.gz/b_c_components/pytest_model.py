import gc
import os
import time
import requests
import pytest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.options import Options
from py.xml import html
from selenium.webdriver.support.wait import WebDriverWait
from b_c_components.get_b_version.get_version import auto_get_browser_driver
from b_c_components.get_config.get_config import Setting


def pytest_html_results_table_header_private(cells):
    """
    a
    """
    while cells:
        cells.pop(0)
    cells.insert(0, html.th('通过/失败', class_="sortable result initial-sort", col="result"))
    cells.insert(1, html.th('测试用例', class_="sortable", col="name"))
    cells.insert(2, html.th('用例描述', col="name"))
    cells.insert(3, html.th("执行耗时/S", class_="sortable", col="duration"))
    cells.insert(4, html.th("校验内容", col="name"))
    cells.insert(5, html.link(rel_="stylesheet", href_='http://8.141.50.128:5000/static/report/css/animate.min.css'))
    cells.insert(6,
                 html.link(rel_='stylesheet', href_='http://8.141.50.128:5000/static/report/syalert/syalert.min.css'))
    cells.insert(7, html.script(src_='http://8.141.50.128:5000/static/report/js/jquery.min.js'))
    cells.insert(8, html.script(src_='http://8.141.50.128:5000/static/report/syalert/syalert.min.js'))


def pytest_html_results_table_row_private(report, cells):
    """
    a
    """
    if report.when == 'call':
        cells.insert(2, html.td(report.description))
        report_name = report.head_line.split('.')[-1]
        str1 = str()
        # data = get_memory_data()
        if driver.global_instance.get('assess_msg').get(report_name) is None:
            str1 = f'html.div("当前用例被手动跳过·没有校验信息，或同时运行两个完全相同名称的用例导致"),  '
        elif len(driver.global_instance.get('assess_msg').get(report_name)[::-1]) != 0:
            for i in driver.global_instance.get('assess_msg').get(report_name)[::-1]:
                str1 += f'html.div("{i}"), '
        else:
            str1 = f'html.div("没有校验信息"),  '
        cells.insert(4,
                     html.td(html.div('点击查看详情', onClick_=f"syalert.syopen('{report_name}')", style_='color:blue'),
                             html.div(html.div('校验信息', class_='sy-title'),
                                      html.div(*eval(str1), class_='sy-content'),
                                      html.div(html.button('确定', onClick_=f'ok("{report_name}")'), class_='sy-btn'),
                                      class_='sy-alert sy-alert-alert animated', sy_enter_='zoomIn', sy_leave_='zoomOut',
                                      sy_type_='alert', sy_mask_='true', id_=f'{report_name}'
                                      )
                             )
                     )
        del str1
        cells.pop()


def pytest_runtest_makereport_private(item, outcome):
    """
    Extends the PyTest Plugin to take and embed screenshot in html_str report, whenever test fails.
    :param outcome:
    :param driver:
    :param item:
    """
    pytest_html = item.config.pluginmanager.getplugin('html')
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    report.nodeid = report.nodeid.encode("utf-8").decode("unicode_escape")
    extra = getattr(report, 'extra', [])
    if report.when == 'call' or report.when == "setup":
        if report.when == 'setup':
            driver.global_instance['case_name'] = item.name
        if report.outcome == 'failed':
            xfail = hasattr(report, 'wasxfail')
            if (report.skipped and xfail) or (report.failed and not xfail):
                try:
                    if hasattr(driver, 'img_dict'):
                        for def_name in driver.img_dict.keys():
                            if report.head_line[len(report.head_line) - len(def_name):] == def_name:
                                img_list = driver.img_dict.get(def_name)
                                for i in img_list:
                                    html_str = f'<a href = "{i}" target=blank ><img target=_blank src="{i}" alt="screenshot" style="width:304px;height:228px;" οnclick="window.open(this.src)" align="right"/></a>'
                                    extra.append(pytest_html.extras.html(html_str))
                                    report.extra = extra
                            else:
                                continue
                except Exception as e:
                    print(e)


def pytest_html_report_title_private(report):
    """
    a
    """
    if hasattr(pytest, 'report_title'):
        if hasattr(pytest, 'browser_language'):
            if pytest.browser_language == 'en,en_US':
                # pytest.browser_language = 'en,en_US'
                report.title = "测试报告·英文浏览器环境"
    else:
        report.title = "测试报告·中文浏览器环境"


def web_driver_initialize_private(case_data=None):
    """

    :return:
    """
    global driver
    config_framework_path = os.environ.get('config_path')
    application_path = os.environ.get('config_path').split('config_framework.ini')[0]
    os.environ.setdefault('application_path', application_path)
    config = Setting(config_framework_path)
    chrome = config.get_setting('chrome_option', 'chrome')
    chrome_options = Options()
    if chrome == 'M':
        argument_list = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--ignore-certificate-errors',
            '--window-size=500,900'
        ]
        chrome_options._arguments = argument_list

        simulator_name = config.get_setting('chrome_option', 'simulator_name')
        chrome_options.experimental_options.update(mobileEmulation={'deviceName': simulator_name})

    elif chrome == 'PC':
        argument_list = [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--ignore-certificate-errors',
        ]
        chrome_options._arguments = argument_list

    elif chrome == 'custom':
        chrome_custom_list = eval(config.get_setting('chrome_option', 'chrome_custom_list'))
        chrome_options._arguments = chrome_custom_list
        experimental_options_list = eval(config.get_setting('chrome_option', 'experimental_options'))
        while experimental_options_list:
            chrome_options.experimental_options.update(experimental_options_list.pop(0))
    chrome_options.experimental_options.update(w3c=False)
    caps = {
        'browserName': 'chrome',
        'loggingPrefs': {
            'browser': 'ALL',
            'driver': 'ALL',
            'performance': 'ALL',
        },
        'goog:chromeOptions': {
            'perfLoggingPrefs': {
                'enableNetwork': True,
            },
            'w3c': False,
        },
    }
    browser_language = config.get_setting('chrome_option', 'browser_language')
    if browser_language:
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': browser_language})
        pytest.browser_language = browser_language
    else:
        chrome_options.experimental_options.update(prefs={'intl.accept_languages': 'en,en_US'})
        pytest.browser_language = browser_language
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
    if hasattr(pytest, 'browser_language'):
        chrome_options.add_experimental_option('prefs', {'intl.accept_languages': pytest.browser_language})
    driver = webdriver.Chrome(
        auto_get_browser_driver(config_framework_path),
        desired_capabilities=caps,
        options=chrome_options)
    driver.global_instance = {}
    if os.environ.get('environment') is not None:
        config.set_data('environment_data', 'environment', os.environ.get('environment'))
        environment = os.environ.get('environment')
        driver.global_instance.update(environment=environment)
    else:
        environment = config.get_setting('environment_data', 'environment')
        os.environ.setdefault('environment', environment)
        driver.global_instance.update(environment=environment)

    driver.implicitly_wait(config.get_int('explicit_waiting', 'implicitly_wait'))
    driver.global_instance.update(config=config)
    driver.global_instance.update(assess_msg={})
    if case_data is not None:
        if environment == 'prod':
            driver.global_instance.update(case_data_dict=case_data.prod_cases_data_dict)
            driver.global_instance.update(tools_data=case_data.prod_tools_data)

        elif environment == 'test':
            driver.global_instance.update(case_data_dict=case_data.test_cases_data_dict)
            driver.global_instance.update(tools_data=case_data.test_tools_data)
    return driver


def cases_setup_private(driver):
    """

    :param driver:
    :return:
    """

    driver.global_cases_instance = {}
    driver.global_cases_instance.update(network_data=[])
    return driver


def pytest_assume(driver, expected_results, actual_results, msg):
    """
    断言
    :param driver:
    :param expected_results: 预期结果
    :param actual_results: 实际结果
    :param msg
    """
    case_name = driver.global_instance['case_name']

    screenshots = pytest.assume(
        expected_results == actual_results,
        f"预期结果与实际结果不一致：预期结果:{expected_results}   实际结果:{actual_results}")
    results_msg = f" : [不通过]" if not screenshots else ' : [通过]'
    if not hasattr(driver.global_instance['assess_msg'], case_name):
        driver.global_instance['assess_msg'][case_name] = []

    driver.global_instance['assess_msg'][case_name].append(msg + results_msg)
    return screenshots


def pytest_assume_contain(driver, expected_results, actual_results, msg):
    """
    断言
    :param driver:
    :param expected_results: 预期结果
    :param actual_results: 实际结果
    :param msg
    """
    case_name = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]
    screenshots = pytest.assume(
        expected_results in actual_results,
        f"预期结果与实际结果不一致：预期结果:{expected_results}   实际结果:{actual_results}")
    results_msg = f" : [不通过]" if not screenshots else ' : [通过]'
    driver.global_instance.get('assess_msg').append(
        {case_name: msg + results_msg})
    return screenshots


def set_screenshots(driver):
    """
    调用此方法进行截图
    driver:
    """
    case_name = driver.global_instance['case_name']
    if not hasattr(driver, 'img_dict'):
        driver.img_dict = dict()
    if driver.img_dict.get(case_name) is None:
        driver.img_dict[case_name] = list()
    file_name = case_name + '_' + 'No.' + str(int(time.time() * 1000)) + ".png"
    headers = {
        'Cookie': 'put_img_key=test'
    }
    data = {
        'img_base64_data': driver.get_screenshot_as_base64(),
        'img_name': file_name
    }
    r = requests.post('http://8.141.50.128:80/put_img_base64', json=data, headers=headers)
    file_name = 'http://8.141.50.128:80' + r.json().get('url')

    driver.img_dict[case_name].append(file_name)


def explicit_waiting(driver, element_str, wait_time=None, poll_frequency=None, element_attribute=None):
    """
    :param driver:
    :param element_str:
    :param wait_time: 默认值20，即配置文件不传、调用不传
    :param poll_frequency: 默认值0.5，即配置文件不传、调用不传
    :param element_attribute
    :return:
    """
    if wait_time is None:
        wait_time = driver.global_instance.get('config').get_int('explicit_waiting', 'timeout')
    if poll_frequency is None:
        poll_frequency = driver.global_instance.get('config').get_int('explicit_waiting', 'poll_frequency')
    timeout = 20 if wait_time is None else wait_time
    poll_frequency = 0.5 if poll_frequency is None else poll_frequency
    wait = WebDriverWait(driver, timeout, poll_frequency)
    if waiting_loading(driver):
        wait.until(lambda x: x.find_element_by_xpath(element_str))
    if element_attribute is not None:
        the_timer = int(time.time())
        while True:
            if the_timer + wait_time <= int(time.time()):
                break
            value = driver.find_element_by_xpath(element_str).get_attribute(element_attribute.get('key'))
            if value == element_attribute.get('value'):
                break
            else:
                continue


def waiting_loading(driver, element=None):
    """
    等待loading消失
    """
    if element is None:
        element = '//*[@id="bs-main"]/div/div[1]'
    the_timer = int(time.time())
    timeout = driver.global_instance.get('config').get_int('explicit_waiting', 'timeout')
    timeout = 20 if timeout is None else timeout

    while True:
        if the_timer + timeout <= int(time.time()):
            break
        if isElementExist(driver, element):

            if driver.find_element_by_xpath(element).get_attribute(
                    'className') == 'loading loading_is-show' and driver.find_element_by_xpath(element).is_displayed():
                time.sleep(0.5)
            else:
                return True
        else:
            return True
    return False


def isElementExist(driver, element_str):
    """

    :param driver:
    :param element_str:
    :return:
    """

    implicitly_wait_int = driver.global_instance.get('config').get_int(
        'explicit_waiting',
        'implicitly_wait')
    driver.implicitly_wait(1)
    if len(driver.find_elements_by_xpath(element_str)) != 0:
        driver.implicitly_wait(implicitly_wait_int)
        return True
    else:
        driver.implicitly_wait(implicitly_wait_int)
        return False


# 判断元素是否存在
def is_element_existence(driver, element):
    """
    判断页面的考核项旁边是否存在...
     :param driver:
     :param element: xpath地址
     :return: 存在为True，不存在为False
    """
    return isElementExist(driver, element)


def get_element_visible(driver, element):
    """
    将元素拉取到可视范围内
    :param driver:
    :param element:
    """
    driver.execute_script("arguments[0].scrollIntoView(false);", element)
    time.sleep(0.5)



