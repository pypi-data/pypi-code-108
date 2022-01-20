import json
import random
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.command import Command
from b_c_components.Intercept_requests.selenium_network import info, get_network_data
from b_c_components.custom_module.custom_exception import Configuration_file_error
from b_c_components.get_environment import get_environment_data, get_host
from b_c_components.pytest_model import *


def login(username, password, driver):
    """
    登陆，返回cookie
    """
    session = requests.session()
    login_data = {
        "UserName": f"{username}",
        "Password": f"{password}",
        "LoginType": "0",
        "Remember": "true",
        "IsShowValCode": "false",
        "ValCodeKey": ""}
    try:
        italent_url = get_environment_data(driver).get('italent_url')
        r = session.post(
            url=italent_url + '/Account/Account/LogInITalent',
            data=login_data)
        if r.status_code == 200:
            if json.loads(r.text).get('Code') == 1:
                driver.get(italent_url)
                driver.add_cookie({'domain': get_host(driver).get('account'),
                                   'name': 'ssn_Tita_PC',
                                   'value': r.cookies.get('Tita_PC')})
                driver.add_cookie(
                    {'name': 'Tita_PC', 'value': r.cookies.get('Tita_PC')})
                driver.add_cookie(
                    {'name': 'Tita_PC', 'value': r.cookies.get('Tita_PC')})
                driver.get(italent_url)
    except Exception as e:
        raise e


def login_interface(username, password, environment):
    """
    :param username:
    :param password:
    :param environment:
    """
    session = requests.session()
    login_data = {
        "UserName": f"{username}",
        "Password": f"{password}",
        "LoginType": "0",
        "Remember": "true",
        "IsShowValCode": "false",
        "ValCodeKey": ""}
    italent_url = get_environment_data(environment=environment).get('italent_url')
    r = session.post(url=italent_url + '/Account/Account/LogInITalent', data=login_data)
    if r.status_code == 200:
        return session
    else:
        return Configuration_file_error(msg=r.text)


def unfinished_transactions(driver, transaction_type, transaction_name):
    """
    cloud待办的处理
    transaction_type 待办所属产品
    transaction_name 以绩效为例，transaction_name代表活动
    """
    cookie = ''
    cookie_list = driver.get_cookies()
    driver.global_cases_instance.update(BSGlobal={})
    time.sleep(0.5)
    driver.global_cases_instance.get('BSGlobal').update(
        tenantInfo=driver.execute_script('return BSGlobal.tenantInfo'))
    driver.global_cases_instance.get('BSGlobal').update(
        userInfo=driver.execute_script('return BSGlobal.userInfo'))
    ssn_Tita_PC = ''
    for i in cookie_list:
        if i.get('name') == 'Tita_PC':
            cookie = f'{i.get("name")}={i.get("value")}' + \
                     f'; {"ssn_Tita_PC"}={i.get("value")}'
            ssn_Tita_PC = i.get("value")
            break
    headers = {
        'Cookie': cookie
    }
    tenantId = str(driver.global_cases_instance.get(
        'BSGlobal').get('tenantInfo').get('Id'))
    userId = str(driver.global_cases_instance.get(
        'BSGlobal').get('userInfo').get('userId'))
    session = requests.session()
    italent_url = get_environment_data(driver).get('italent_url')
    url = f'{italent_url}/api/v3/{tenantId}/{userId}/todo/Get?app_id=-1&deadline=&blackTodoIds=&page_size=10&status=1&__t={round(time.time() * 1000)}'
    all_transactions = json.loads(
        session.get(
            url=url,
            headers=headers).text).get('data').get('todos')
    cloud_url = get_environment_data(driver).get('cloud_url').split('://')[1]
    driver.add_cookie(
        {'domain': cloud_url, 'name': 'ssn_Tita_PC', 'value': ssn_Tita_PC})
    for i in all_transactions:
        if transaction_type == i.get('appName'):
            if transaction_name != "" and transaction_name in i.get('content'):
                driver.get(url='https:' + i.get('objUrl'))
                break


def go_to_menu(driver, menu_name):
    """
    进入菜单
    menu_name: 菜单名称，默认菜单传应用名称，非默认菜单传应用名称_菜单名称
    """
    cloud_host = get_host(driver).get('cloud')
    driver.add_cookie({'domain': cloud_host,
                       'name': 'ssn_Tita_PC',
                       'value': driver.get_cookie('Tita_PC').get('value')})
    driver.add_cookie({'domain': cloud_host,
                       'name': 'Tita_PC',
                       'value': driver.get_cookie('Tita_PC').get('value')})
    menu_mapping = requests.get('http://8.141.50.128:80/static/json_data/menu_mapping.json').json()
    host_url = get_environment_data(driver).get('cloud_url')
    driver.get(host_url + menu_mapping.get(menu_name))


def get_form_view(driver):
    """
    获取表单信息
    """
    fields_to_operate_on_list = []
    network_data = info(driver)
    network_data.reverse()
    datasource_data = []
    for data in network_data:
        url = data.get('request').get('url')
        if '/api/v2/data/datasource' in url:
            # 获取字段对应数据源
            datasource_data = json.loads(data.get('response_data').get('body'))
            break
    for data in network_data:
        # 解析formView接口，获取所有表单字段
        url = data.get('request').get('url')
        if '/api/v2/UI/FormView' in url:
            # 在这里获取所有需要操作的字段
            for sub in json.loads(
                    data.get('response_data').get('body')).get('sub_cmps'):
                for field in sub.get('sub_cmps'):
                    if field.get('cmp_data').get('showdisplaystate') == 'readonly' and field.get(
                            'cmp_data').get('required') is True:
                        dict_data = {}
                        for data_source in datasource_data:
                            if field.get('cmp_data').get(
                                    'datasourcename') == data_source.get('key'):
                                dict_data['dataSourceResults'] = data_source.get(
                                    'dataSourceResults')
                                break
                        dict_data.update({
                            'cmp_id': field.get('cmp_id'),
                            'cmp_label': field.get('cmp_label'),
                            'cmp_name': field.get('cmp_name'),
                            'cmp_type': field.get('cmp_type'),
                            'cmp_data': field.get('cmp_data')
                        })
                        fields_to_operate_on_list.append(dict_data)
    return fields_to_operate_on_list


def input_operation(driver, input_xpath, input_content=None):
    """
    输入框操作，对输入框进行输入值
    :param driver: driver实例
    :param input_xpath: 输入框的xpath路径
    :param input_content: 输入框自定义的填写
    :return:
    """
    element = driver.find_element_by_xpath(input_xpath)
    element.clear()
    if input_content:
        element.send_keys(input_content)
    else:
        element.send_keys(
            '自动化数据' + str(int(time.time())))
    driver.execute_script("arguments[0].blur();", element)


def drop_down_list_operation(driver, list_xpath, is_multiple, select_content=None):
    """
    下拉选项类型的选择操作
    :param driver: 实例
    :param list_xpath: 下拉控件的xpath路径
    :param is_multiple: True 多选，False单选
    :param select_content: 选择的选项
    :return:
    """
    driver.find_element_by_xpath(list_xpath).click()
    if is_multiple:
        if select_content:
            for select_name in select_content:
                driver.find_element_by_xpath(f"//span[@class='form-item__label' and text()='{select_name}']").click()
        else:
            driver.find_element_by_xpath(f"//span[@class='form-item__label']").click()
        driver.find_element_by_xpath(
            '//div[@id="DropdownList_ul"]//button[@class="btn btn_default btn_sm"]').click()
    else:
        if select_content:
            li_xpath = f"//ul[@class='dropdown__list a-height-spread']/li/span[text()='{select_content}']"
        else:
            li_xpath = "//ul[@class='dropdown__list a-height-spread']/li"
        driver.find_element_by_xpath(li_xpath).click()


def user_select_operation(driver, user_select_xpath, users_name=None):
    """
    人员选择控件
    :param driver: 实例
    :param user_select_xpath: 人员选择控件点击的xpath路径
    :param users_name: 选择的人员
    :return:
    """
    driver.find_element_by_xpath(user_select_xpath).click()
    if users_name:
        user_name_input_xpath = "//div[@class='us-multi-container']//input"
        for user_name in users_name:
            driver.find_element_by_xpath(user_name_input_xpath).clear()
            driver.find_element_by_xpath(user_name_input_xpath).send_keys(user_name)
            select_name_xpath = f"//ul[@class='us-item-top']/li//em[text()='{user_name}']"
            driver.find_element_by_xpath(select_name_xpath).click()
    else:
        select_name_xpath = f"//ul[@class='us-item-top']/li/"
        driver.find_element_by_xpath(select_name_xpath).click()
    driver.find_element_by_xpath(
        '//div[@class="us-container"]//span[@class="base-bg-ripple  base-btns-bgc-small  "]').click()


def digit_text_operation(driver, input_xpath, input_content=None):
    """
    数值类型输入框操作
    :param driver: driver: 实例
    :param input_xpath: 输入框xpath路径
    :param input_content: 输入框内容
    :return:
    """
    element = driver.find_element_by_xpath(input_xpath)
    element.clear()
    if input_content:
        element.send_keys(input_content)
    else:
        input_num = random.randint(1, 100)
        element.send_keys(input_num)
    driver.execute_script("arguments[0].blur();", element)


def data_time_operation(driver, data_time_xpath, date_format, data_time_content=None):
    """
    日期类型控件的操作
    :param driver: 实例
    :param data_time_xpath: 日期控件的点击xpath路径
    :param date_format: 日期类型
    :param data_time_content: 日期输入内容
    :return:
    """
    driver.find_element_by_xpath(data_time_xpath).click()
    if data_time_content:
        if date_format == 'yyyy/MM/dd HH:mm:ss':
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(
                data_time_content)
            driver.find_element_by_xpath("//a[@class='ant-calendar-ok-btn' and @role='button']").click()
        elif date_format == 'yyyy/MM/dd':
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(Keys.CONTROL,
                                                                                                        'a')
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(Keys.DELETE)
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(
                data_time_content)
            driver.find_element_by_xpath("//div[@class='modal-pop__header']").click()
            time.sleep(1)
        elif date_format == 'yyyy/MM':
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(
                data_time_content)
        elif date_format == 'HH:mm':
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input  head-input ']").send_keys(
                data_time_content)
            time.sleep(1)
            driver.find_element_by_xpath(data_time_xpath).click()
    else:
        if date_format == 'yyyy/MM/dd HH:mm:ss':
            driver.find_element_by_xpath("//a[@class='ant-calendar-today-btn ' and text()='此刻']").click()
            driver.find_element_by_xpath("//a[@class='ant-calendar-ok-btn' and @role='button']").click()
        elif date_format == 'yyyy/MM/dd':
            driver.find_element_by_xpath("//a[@class='ant-calendar-today-btn ' and text()='今天']").click()
        elif date_format == 'yyyy/MM':
            driver.find_element_by_xpath("//a[@class='ant-calendar-today-btn ' and text()='本月']").click()
        elif date_format == 'HH:mm':
            driver.find_element_by_xpath(
                "//div[@class='ant-time-picker-panel-inner']//li[@class='ant-time-picker-panel-select-option-selected']").click()
            driver.find_element_by_xpath("//div[@class='modal-pop__header']").click()


def upload_file_operation(driver, file_input_xpath, file_path=None):
    """
    上传控件的操作
    :param driver:实例
    :param file_input_xpath:文件input的xpath路径
    :param file_path:上传文件的路径
    :return:
    """
    if file_path:
        driver.find_element_by_xpath(file_input_xpath).send_keys(file_path)
    else:
        input_file = os.environ.get('application_path') + driver.global_instance.get(
            'case_data').cases_data_dict.upload_file.get('file_path')
        driver.find_element_by_xpath(file_input_xpath).send_keys(input_file)


def option_form(driver, fields_to_operate_on_list, **kwargs):
    """
    支持文本、富文本、单选下拉、多选下拉、数值输入框、日期、日期时间、年月、时间、上传类型
    BC_TextBox、BC_TextArea、BC_DropDownList、BC_UserSelect、BC_DigitText、BC_DateTime、BC_Time、BC_FileUploader
    :param driver: 实例
    :param fields_to_operate_on_list: 必填字段信息
    :param kwargs:
    :return:
    """
    if kwargs.keys() is not None:
        pass
    enter_iframe(driver, '//*[@class="modal-pop"]')
    for field in fields_to_operate_on_list:
        """
        表单填充
        """
        if field.get('cmp_type') == 'BC_TextBox':
            """
            文本输入框类型
            """
            key_value = field.get('cmp_label')
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//input"
            input_text = None
            if key_value in kwargs.keys():
                input_text = kwargs.get(key_value)
            input_operation(driver, title_xpath, input_text)
        elif field.get('cmp_type') == 'BC_TextArea':
            """
            富文本类型
            """
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//textarea"
            input_text = None
            key_value = field.get('cmp_label')
            if key_value in kwargs.keys():
                input_text = kwargs.get(key_value)
            input_operation(driver, title_xpath, input_text)
        elif field.get('cmp_type') == 'BC_DropDownList':
            """
            下拉类型
            """
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//div[@class='form-item__control ']//input/.."
            key_value = field.get('cmp_label')
            is_multiple = False
            if 'multiple' in field.get('cmp_data').keys():
                is_multiple = field.get('cmp_data').get('multiple')
            select_name = None
            if key_value in kwargs.keys():
                select_name = kwargs.get(key_value)
            drop_down_list_operation(driver, title_xpath, is_multiple, select_name)
        elif field.get('cmp_type') == 'BC_UserSelect':
            """人员选择"""
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//input/.."
            key_value = field.get('cmp_label')
            users_name = None
            if key_value in kwargs.keys():
                users_name = kwargs.get(key_value)
            user_select_operation(driver, title_xpath, users_name)
        elif field.get('cmp_type') == 'BC_DigitText':
            """
            数值输入框
            """
            key_value = field.get('cmp_label')
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//input"
            input_text = None
            if key_value in kwargs.keys():
                input_text = kwargs.get(key_value)
            digit_text_operation(driver, title_xpath, input_text)
        elif field.get('cmp_type') in ['BC_DateTime', 'BC_Time']:
            """时间选择"""
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//input/.."
            key_value = field.get('cmp_label')
            date_format = field.get('cmp_data').get('data_format')
            input_date = None
            if key_value in kwargs.keys():
                input_date = kwargs.get(key_value)
            data_time_operation(driver, title_xpath, date_format, input_date)
        elif field.get('cmp_type') == 'BC_FileUploader':
            title_xpath = f"(//div[@class='form-item__title ']/a[@class='form-item__required'])" \
                          f"[{fields_to_operate_on_list.index(field) + 1}]/../..//input"
            key_value = field.get('cmp_label')
            if key_value in kwargs.keys():
                input_file = kwargs.get(key_value)
            else:
                input_file = None
            upload_file_operation(driver, title_xpath, input_file)
    driver.switch_to_default_content()


def click_check_index(driver, list_index):
    """
    点击列表上的复选框，支持int和list，int单选，list多选
    """
    check_str_path = '//*[@name="checkboxPro"]'
    if isinstance(list_index, int):
        element = driver.find_elements_by_xpath(check_str_path)[list_index - 1]
        element.click()
    elif isinstance(list_index, list):
        for i in list_index:
            element = driver.find_elements_by_xpath(check_str_path)[i - 1]
            element.click()


def go_to_data_details(driver, details_page_name, details_page_id):
    """
    进入列表数据详情
    :param driver: driver: 实例
    :param details_page_name: 哪个产品的详情页
    :param details_page_id: 详情页的id('新增接口有返回')
    """
    host_url = get_environment_data(driver).get('cloud_url')
    details_page_mapping = requests.get(
        'http://8.141.50.128:80/static/json_data/details_page_mapping.json').json()
    if details_page_mapping.get(details_page_name):
        interface_url = details_page_mapping.get(details_page_name)
        headers = {
            'Pragma': 'no-cache'
        }
        driver.get(host_url + interface_url + details_page_id)
    else:
        raise Configuration_file_error(msg='mappings文件中没有对应的详情页路径')


def check_list_data(driver):
    """
    校验列表数据当前分页中的指定数据或所有的所有字段是否有值
    """
    list_elements = list()
    for list_element in driver.find_elements_by_xpath('//*[@class="z-table"]/div/div'):
        col_element_data = dict()
        for col_element in list_element.find_elements_by_xpath('./div'):
            if col_element.get_attribute('name') == 'CreatedBy':
                col_element_data[col_element.get_attribute('name')] = \
                    col_element.find_element_by_xpath('./div/div/span[2]').text
                continue
            col_element_data[col_element.get_attribute('name')] = col_element.text
        list_elements.append(col_element_data)
    network_data = info(driver)
    tab_list_data = None
    for data in network_data:
        if '/api/v2/UI/TableList' in data.get('request').get('url'):
            tab_list_data = json.loads(data.get('response_data').get('body'))
            break
    if tab_list_data is not None:
        for biz_data in tab_list_data.get('biz_data'):
            col_list = list_elements.pop(0)
            failure_data = [c for c in list(col_list.keys()) if c not in list(biz_data.keys())]
            if failure_data:
                for data in failure_data:
                    pytest_assume(driver, col_list.get(data), list(biz_data.keys()), '列表中的字段在接口中不存在即没有数据')
            else:
                pytest_assume(driver, True, True, '对比当前页面的所有字段，数据正确')
                failure_data = [d for d in list(col_list.keys()) if col_list.get(d) not in biz_data.get(d).get('value')]
                if 'CreatedBy' in failure_data:
                    failure_data.pop(failure_data.index('CreatedBy'))
                    CreatedBy = biz_data.get('CreatedBy').get('text').split('(')[0]
                    pytest_assume(driver, col_list.get('CreatedBy'), CreatedBy, '创建人字段值正确')
                if failure_data:
                    for data in failure_data:
                        pytest_assume(driver, col_list.get(data), biz_data.get(data).get('value'),
                                      '列表中的字段对应值在接口中不存在即没有数据')
                else:
                    pytest_assume(driver, True, True, '对比当前页面的所有字段的值，数据存在')
                continue


def filter_item(driver, filter_name, *args, **kargs):
    """
    对筛选条件进行操作
    :param driver: driver: 实例
    :param filter_name: 筛选条件的名称，->1为角标标识
    """
    if "->" in filter_name:
        filter_name = filter_name.split('->', 1)
        filter_xpath = f"(//div[@class='searchform clearfix']//div[@class='field-left']//span[text()='{filter_name[0]}'])['{filter_name[1]}']"
        filter_info = get_filter_info(driver, filter_name[0], filter_name[1])
    else:
        filter_xpath = f"//div[@class='searchform clearfix']//div[@class='field-left']//span[text()='{filter_name}']"
        filter_info = get_filter_info(driver, filter_name)
    filter_cmp_type = filter_info.get('cmp_type')
    if filter_cmp_type == 'BC_TextBox':
        driver.find_element_by_xpath(filter_xpath).click()
        input_operation(driver, "//*[@id='inputText']", input_content=args)
        driver.find_element_by_xpath('//div[@class="TextBoxShow"]//span[@class="base-btn-title"]/..').click()
    elif filter_cmp_type == 'BC_UserSelect':
        user_select_operation(driver, filter_xpath, users_name=args)
    elif filter_cmp_type == 'BC_DropDownList':
        is_multiple = False
        if 'multiple' in filter_info.get('cmp_data').keys():
            is_multiple = filter_info.get('cmp_data').get('multiple')
        drop_down_list_operation(driver, filter_xpath, is_multiple, args)
    elif filter_cmp_type == 'BC_DateTimeRange':
        driver.find_element_by_xpath(filter_xpath).click()
        for x in kargs.keys():
            driver.find_element_by_xpath(
                f"//input[@class='ant-calendar-range-picker ant-input input-create-picker ' and @placeholder='{x}']/..").click()
            input_element = driver.find_element_by_xpath("//input[@class='ant-calendar-input ']")
            input_element.send_keys(Keys.CONTROL + 'a')
            input_element.send_keys(Keys.DELETE)
            input_element.clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input ']").send_keys(kargs.get(x))
            driver.find_element_by_xpath("//a[@class='ant-calendar-ok-btn' and @role='button']").click()
        driver.find_element_by_xpath(
            '//div[@class="dateTime-range-container-show"]//span[@class="base-btn-title"]/..').click()


def advanced_filter_item(driver, filter_name, *args, **kargs):
    """
    筛选条件如果有名称相同的，用->来指明角标，1代表第1个，2代表第2个
    :param driver:实例
    :param filter_name: 筛选项名称
    :param args:
    :param kargs:
    :return:
    """
    if "->" in filter_name:  # 判断该参数是否含有->
        filter_name = filter_name.split('->', 1)  # 根据->分割，得到列表['筛选名称',1]
        filter_info = get_filter_info(driver, filter_name[0], filter_name[1])
        filter_name_xpath = f"(//div[@class='AdvancedFilterInfo clearfix']//label[text()='{filter_name[0]}'])['{filter_name[1]}']"
    else:
        filter_info = get_filter_info(driver, filter_name)
        filter_name_xpath = f"//div[@class='AdvancedFilterInfo clearfix']//label[text()='{filter_name}']"
    advanced_filter_title = "//div[@class='searchform clearfix']//p[@class='AdvancedFilterTitle']"
    filter_cmp_type = filter_info.get('cmp_type')
    driver.find_element_by_xpath(advanced_filter_title).click()  # 点击高级筛选条件
    if filter_cmp_type == "BC_TextBox":
        input_operation(driver, f"{filter_name_xpath}/../..//input", input_content=args)
    elif filter_cmp_type == 'BC_UserSelect':
        user_select_operation(driver, f"{filter_name_xpath}/../..//ul", users_name=args)
    elif filter_cmp_type == 'BC_DropDownList':
        is_multiple = False
        if 'multiple' in filter_info.get('cmp_data').keys():
            is_multiple = filter_info.get('cmp_data').get('multiple')
        drop_down_list_operation(driver, f"{filter_name_xpath}/../..//ul", is_multiple, args)
    elif filter_cmp_type == 'BC_DateTimeRange':
        for key in kargs:
            driver.find_element_by_xpath(
                f"{filter_name_xpath}/../../..//input[@placeholder='{key}']/..").click()
            input_element = driver.find_element_by_xpath("//input[@class='ant-calendar-input ']")
            input_element.send_keys(Keys.CONTROL + 'a')
            input_element.send_keys(Keys.DELETE)
            input_element.clear()
            driver.find_element_by_xpath("//input[@class='ant-calendar-input ']").send_keys(kargs.get(key))
            driver.find_element_by_xpath("//a[@class='ant-calendar-ok-btn' and @role='button']").click()
    driver.find_element_by_xpath(
        '//div[@class="btnAllBorder"]//span[@class="base-btn-title"]/..').click()


def get_filter_info(driver, filter_name, filter_name_index=None):
    """
    :param driver: 实例
    :param filter_name: 筛选名称
    :param filter_name_index: 如果有重复的筛选名称，取第几个
    :return:
    """
    driver.refresh()  # 重新获取index_page接口
    network_data = info(driver)
    network_data.reverse()
    for data in network_data:
        url = data.get('request').get('url')
        if '/api/v2/UI/IndexPage' in url:
            # 获取字段对应数据源
            response_data = json.loads(data.get('response_data').get('body'))
            filter_sub_cmps_list = response_data.get('sub_cmps').get('active_view').get('sub_cmps').get(
                'search_form').get('sub_cmps')
            count = 0
            for filter_sub_cmp in filter_sub_cmps_list:
                cmp_label = filter_sub_cmp.get('cmp_label')
                if cmp_label == filter_name:
                    if filter_name_index:
                        count = count + 1
                        if filter_name_index == count:
                            return filter_sub_cmp
                    return filter_sub_cmp


def enter_iframe(driver, element_str):
    """
    处理iframe跳转
    :param element_str
    :param driver
    """
    for i in driver.find_elements_by_xpath('//iframe'):
        driver.switch_to_frame(i)
        if isElementExist(driver, element_str):
            return
        else:
            driver.switch_to_default_content()
            continue


def form_button_click(driver, button_name):
    """
    :param driver
    :param button_name
    专用于表单区域的按钮点击
    """
    form_element_str = requests.get('http://8.141.50.128:5000/static/json_data/button_xpath_str.json'
                                    ).json().get('form_button_click')
    button_click(driver, form_element_str, button_name)


def list_button_click(driver, button_name):
    """
    :param driver
    :param button_name
    专用于表单区域的按钮点击
    """
    form_element_str = requests.get('http://8.141.50.128:5000/static/json_data/button_xpath_str.json'
                                    ).json().get('list_button_click')
    button_click(driver, form_element_str, button_name)


def view_tab_button_click(driver, button_name):
    """
    :param driver
    :param button_name
    专用于视图切换的按钮点击
    """
    form_element_str = requests.get('http://8.141.50.128:5000/static/json_data/button_xpath_str.json'
                                    ).json().get('view_tab_button_click')
    button_click(driver, form_element_str, button_name)


def view_button_click(driver, button_name):
    """
    专用于视图功能的按钮点击
    """
    form_element_str = requests.get('http://8.141.50.128:5000/static/json_data/button_xpath_str.json'
                                    ).json().get('view_button_click')
    button_click(driver, form_element_str, button_name)


def details_page_button_click(driver, button_name):
    """
    专用于详情页功能的按钮点击
    """
    form_element_str = requests.get('http://8.141.50.128:5000/static/json_data/button_xpath_str.json'
                                    ).json().get('details_page_button_click')
    button_click(driver, form_element_str, button_name)


def button_click(driver, form_element_str, button_name):
    """
    :param driver driver实例
    :param form_element_str 对应区域的str
    :param button_name 按钮名称
    """
    explicit_waiting(driver, '//iframe')
    time.sleep(0.5)
    if not isElementExist(driver, form_element_str):
        enter_iframe(driver, form_element_str)
    form_element = driver.find_element_by_xpath(form_element_str)
    for i in form_element.find_elements_by_xpath(f'//*[text()="{button_name}"]'):
        try:
            driver.execute_script("arguments[0].click();", i)
            time.sleep(0.5)
            break
        except ElementClickInterceptedException:
            continue
    driver.switch_to_default_content()


def get_form_list_info(driver):
    """
    获取勾选列表弹窗的列表数据
    :param driver:
    :return: 列表数据信息
    """
    network_data = info(driver)
    network_data.reverse()
    for data in network_data:
        url = data.get('request').get('url')
        if '/api/v2/UI/TableList' in url:
            get_api_body = json.loads(
                data.get('response_data').get('body'))
            biz_data = get_api_body.get('biz_data')
            return biz_data


def form_list_operation(driver, **kwargs):
    """
    :param driver:
    :param kwargs: {'字段名称':'字段值'}例如：字典{'TypeId':1} 勾选TypeId字段为1的数据
    :return:
    """
    check_box = "//div[@class='fixWrapperLeft']//div[@class='cklist-checkbox cklist-optional table_list']"
    biz_data = get_form_list_info(driver)
    if biz_data:
        for index, biz in enumerate(biz_data):
            if kwargs:
                type_name,item_type = kwargs
                value = biz.get(type_name).get("value")
                if int(value) == item_type:
                    check_box = f"(//div[@class='fixWrapperLeft']//div[@class='cklist-checkbox cklist-optional table_list'])[{index+1}]"
                    driver.find_element_by_xpath(check_box).click()
                    break
            else:
                driver.find_element_by_xpath(check_box).click()
                break
