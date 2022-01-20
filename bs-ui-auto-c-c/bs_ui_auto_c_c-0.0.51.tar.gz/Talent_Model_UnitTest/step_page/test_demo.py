
from v5_components.page.modlues import *


def test_ghy(web_driver_initialize):
    """
    1
    """
    login('root600684@beisen.com', 'aa123456', web_driver_initialize)
    go_to_menu(web_driver_initialize, '人才模型')
    filter_item(web_driver_initialize, "计分规则", '平均值', '加权平均值')
    filter_item(web_driver_initialize, "名称", "人才模型")
    filter_item(web_driver_initialize, "创建时间", **{'开始时间': '20211116', "截止时间": "20211216"})
    filter_item(web_driver_initialize, "所有者", '管理员', '大区负责人')
    time.sleep(5)


def test_ghy_02(web_driver_initialize):
    """
    1
    """
    login('root600684@beisen.com', 'aa123456', web_driver_initialize)
    go_to_menu(web_driver_initialize, '人才模型')
    advanced_filter_item(web_driver_initialize, "计分规则", '平均值', '加权平均值')
    advanced_filter_item(web_driver_initialize, "名称", "人才模型")
    advanced_filter_item(web_driver_initialize, "所有者", "管理员", "大区负责人")
    advanced_filter_item(web_driver_initialize, "创建时间", **{'开始时间': '20211116', "截止时间": "20211216"})

    time.sleep(5)


def test_ghy_03(web_driver_initialize):
    """
    1
    """
    login('root600684@beisen.com', 'aa123456', web_driver_initialize)
    go_to_menu(web_driver_initialize, '人才模型')
    button_click(web_driver_initialize, "//div[@class='button-list clearfix  ']", "新增")
    fields_to_operate_on_list = get_form_view(web_driver_initialize)
    option_form(web_driver_initialize, fields_to_operate_on_list, **{'人员多选': ['管理员', '大区负责人'],
                                                                     '单选列表': '老虎',
                                                                     '自定义整数类型': '100',
                                                                     '文本类型': '今天是个好天气~'})
    form_button_click(web_driver_initialize, "保存")


def test_add_talent_model(web_driver_initialize):
    """
    新增人才模型
    """

    go_to_menu(web_driver_initialize, '人才模型')
    list_button_click(web_driver_initialize, '新增')
    fields_to_operate_on_list = get_form_view(web_driver_initialize)
    option_form(web_driver_initialize, fields_to_operate_on_list, **{'人才模型': '自动新增人才模型5'})
    form_button_click(web_driver_initialize, '保存')
    enter_iframe(web_driver_initialize, '//*[@class="round-pattern-tips-title"]')
    value = web_driver_initialize.find_element_by_xpath('//*[@class="round-pattern-tips-title"]').text
    data = web_driver_initialize.global_instance.get('case_data').cases_data_dict.add_talent_model_date
    expected_results = data.get('预期结果')
    pytest_assume(web_driver_initialize, expected_results, value, '自动创建活动，页面显示添加成功')


def test_delete_talent_model(web_driver_initialize):
    """
    删除人才模型
    """
    go_to_menu(web_driver_initialize, '人才模型')
    click_check_index(web_driver_initialize, 1)
    list_button_click(web_driver_initialize, '删除')
    list_button_click(web_driver_initialize, '是')
    explicit_waiting(web_driver_initialize, '//*[@class="round-pattern-tips-title"]',
                     element_attribute={'key': 'innerText', 'value': '删除成功'})
    value = web_driver_initialize.find_element_by_xpath('//*[@class="round-pattern-tips-title"]').text
    data = web_driver_initialize.global_instance.get('case_data').cases_data_dict.delete_talent_model_date
    expected_results = data.get('预期结果')
    pytest_assume(web_driver_initialize, expected_results, value, '自动创建活动，页面显示删除成功')



