#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2022/1/11 3:51 下午
# @Author  : zhengyu.0985
# @FileName: autotest_generator.py
# @Software: PyCharm

import os
import json
from string import Template
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')  # logging.basicConfig函数对日志的输出格式及方式做相关配置
logger = logging.getLogger('com.zijie.tests.base.autotest_generator')


class TestGenerator(object):

    @staticmethod
    def rest_generate(rest_test_file_path='',
                      test_class_name='TestXXX',
                      domain_host_url='https://boe-pangle-ssr.bytedance.net',
                      case_info_dict_list=[]):
        """
        :param rest_test_file_path: com.zijie.tests.rest.之后的路径到.py结束。
        :param test_class_name: 测试类的名称，必须以Test开头，以符合PyTest规范。
        :param domain_host_url: Restful请求的域名地址。
        :param case_info_dict_list: 测试用例信息列表，元素要求为dict类型。
        :return:
        """

        # 获取待生成的目标python文件
        template_path = TestGenerator.__get_template_path("rest")
        # py_file_path = template_path + "../../zijie/tests/rest/" + rest_test_file_path
        py_file_path = TestGenerator._get_com_path() + "zijie/tests/rest/" + rest_test_file_path
        py_file = open(py_file_path, 'w')
        # 组装测试类
        setup_file_path = template_path + "restful_setup.template"
        setup_template_file = open(setup_file_path)
        setup_template = Template(setup_template_file.read())
        # setup模版替换
        lines = [setup_template.substitute(
            rest_test_file_path=rest_test_file_path,
            test_class_name=test_class_name,
            domain_host_url=domain_host_url)]

        # 用例模板替换
        lines.extend(TestGenerator._get_test_cases(case_info_dict_list))
        # teardown模板替换
        teardown_file_path = template_path + "restful_teardown.template"
        teardown_template_file = open(teardown_file_path)
        teardown_template = Template(teardown_template_file.read())
        lines.extend(teardown_template.substitute(rest_test_file_path=rest_test_file_path))
        # 输出至python文件并保存。
        py_file.writelines(lines)
        py_file.close()
        logger.info('[Success] Generate %s. ~ ~' % py_file_path)

    @staticmethod
    def rpc_generate(thrift_test_file_path='',
                     test_class_name='TestXXX',
                     thrift_file_name='thrift_file_name',
                     case_info_dict_list=[]):
        """
        :param thrift_test_file_path: com.zijie.tests.thrift.之后的路径到.py结束。
        :param test_class_name: 测试类的名称，必须以Test开头，以符合PyTest规范。
        :param thrift_file_name: thrift文件名。
        :param case_info_dict_list: 测试用例信息列表，元素要求为dict类型。
        :return:
        """

        # 获取待生成的目标python文件
        template_path = TestGenerator.__get_template_path("thrift")
        py_file_path = TestGenerator._get_com_path() + "zijie/tests/thrift/" + thrift_test_file_path
        py_file = open(py_file_path, 'w')
        # 组装测试类
        setup_file_path = template_path + "thrift_setup.template"
        setup_template_file = open(setup_file_path)
        setup_template = Template(setup_template_file.read())
        # setup模版替换
        lines = [setup_template.substitute(
            thrift_test_file_path=thrift_test_file_path,
            test_class_name=test_class_name,
            thrift_file_name=thrift_file_name)]

        # 用例模板替换
        lines.extend(TestGenerator._get_test_cases(case_info_dict_list))
        # teardown模板替换
        teardown_file_path = template_path + "thrift_teardown.template"
        teardown_template_file = open(teardown_file_path)
        teardown_template = Template(teardown_template_file.read())
        lines.extend(teardown_template.substitute(thrift_test_file_path=thrift_test_file_path))
        # 输出至python文件并保存。
        py_file.writelines(lines)
        py_file.close()
        logger.info('[Success] Generate %s. ~ ~' % py_file_path)
        pass

    @staticmethod
    def _get_test_cases(case_info_dict_list):
        lines = []
        if len(case_info_dict_list) == 0:
            pass
        else:
            for case_info_dict in case_info_dict_list:
                lines.append(TestGenerator._get_one_case(case_info_dict))
                lines.append("\n")
        return lines

    @staticmethod
    def _get_one_case(curr_case_dict):
        if type(curr_case_dict) == dict:
            order = 1
            test_method_name = "test_method_name"
            inter_name = "inter_name"
            protocol_type = "HTTP"
            method_name = "thrift_method_name"  # for thrift api only
            inter_path = "/suburi"
            cookie = ""
            http_method = ""
            http_method_call = ""
            param_class_name = ""  # for thrift api only
            if "order" in curr_case_dict.keys():
                order = curr_case_dict['order']
            if "test_method_name" in curr_case_dict.keys():
                test_method_name = curr_case_dict['test_method_name']
            if "inter_name" in curr_case_dict.keys():
                inter_name = curr_case_dict['inter_name']
            if "protocol_type" in curr_case_dict.keys():
                protocol_type = curr_case_dict['protocol_type']
            if "method_name" in curr_case_dict.keys():
                method_name = curr_case_dict['method_name']
            if "inter_path" in curr_case_dict.keys():
                inter_path = curr_case_dict['inter_path']
            if "cookie" in curr_case_dict.keys():
                cookie = curr_case_dict['cookie']
            if "http_method" in curr_case_dict.keys():
                http_method = curr_case_dict['http_method'].lower()
                if http_method == "get":
                    http_method_call = "send_get_request_by_suburi"
                elif http_method == "post":
                    http_method_call = "send_json_post_request_by_suburi"
                else:
                    http_method_call = "不支持GET或POST以外的请求"
                    logger.info("当前用例自动生成仅支持GET和POST请求。")
            if "param_class_name" in curr_case_dict.keys():
                param_class_name = curr_case_dict['param_class_name']
            # 准备组装Template
            # 下面开始判断该用例是否是参数化的
            if "parameters" in curr_case_dict.keys() and len(curr_case_dict['parameters']) > 0:
                parameters = curr_case_dict['parameters']
                if "," in parameters:
                    param_list = parameters.split(",")
                    values_tuples = "("
                    for param in param_list:
                        values_tuples = values_tuples + param.strip() + "_value0, "
                    values_tuples = values_tuples + ")"
                else:
                    values_tuples = "(" + parameters.strip() + "_value0)"
                # 真正开始组装Template
                # 判断是HTTP接口还是THRIFT接口
                if protocol_type.lower() == "http" or protocol_type.lower() == "rest":
                    template_path = TestGenerator.__get_template_path("rest")
                    parameter_case_file_path = template_path + "restful_parameter_case.template"
                    parameter_case_template_file = open(parameter_case_file_path)
                    template = Template(parameter_case_template_file.read())
                    result = template.substitute(
                        order=order,
                        test_method_name=test_method_name,
                        inter_name=inter_name,
                        protocol_type=protocol_type,
                        inter_path=inter_path,
                        cookie=cookie,
                        http_method=http_method,
                        http_method_call=http_method_call,
                        parameters=parameters,
                        values_tuples=values_tuples
                    )
                elif protocol_type.lower() == "thrift" or protocol_type.lower() == "rpc":
                    template_path = TestGenerator.__get_template_path("thrift")
                    parameter_case_file_path = template_path + "thrift_parameter_case.template"
                    parameter_case_template_file = open(parameter_case_file_path)
                    template = Template(parameter_case_template_file.read())
                    result = template.substitute(
                        order=order,
                        test_method_name=test_method_name,
                        inter_name=inter_name,
                        protocol_type=protocol_type,
                        method_name=method_name,
                        cookie=cookie,
                        param_class_name=param_class_name,
                        parameters=parameters,
                        values_tuples=values_tuples
                    )
                else:
                    result = ""
                    logger.warning("当前仅支持接口协议为HTTP和THRIFT。")
            else:  # 该else代表该用例是非参数化执行。
                if protocol_type.lower() == "http" or protocol_type.lower() == "rest":
                    template_path = TestGenerator.__get_template_path("rest")
                    restful_case_file_path = template_path + "restful_case.template"
                    restful_case_template_file = open(restful_case_file_path)
                    template = Template(restful_case_template_file.read())
                    result = template.substitute(
                        order=order,
                        test_method_name=test_method_name,
                        inter_name=inter_name,
                        protocol_type=protocol_type,
                        inter_path=inter_path,
                        cookie=cookie,
                        http_method=http_method,
                        http_method_call=http_method_call
                    )
                elif protocol_type.lower() == "thrift" or protocol_type.lower() == "rpc":
                    template_path = TestGenerator.__get_template_path("thrift")
                    thrift_case_file_path = template_path + "thrift_case.template"
                    thrift_case_template_file = open(thrift_case_file_path)
                    template = Template(thrift_case_template_file.read())
                    result = template.substitute(
                        order=order,
                        test_method_name=test_method_name,
                        inter_name=inter_name,
                        protocol_type=protocol_type,
                        method_name=method_name,
                        cookie=cookie,
                        param_class_name=param_class_name,
                    )
                else:
                    result = ""
                    logger.warning("当前仅支持接口协议为HTTP和THRIFT。")
            return result
        else:
            logger.error('case_info_dict_list的元素不是dict类型。')
            return ""

    @staticmethod
    def __get_template_path(rest_or_thrift):
        return TestGenerator._get_com_path() + "templates/" + rest_or_thrift + "/"

    @staticmethod
    def _get_com_path():
        curr_path = os.getcwd()
        index_of_com = curr_path.find("com")
        if index_of_com != -1:
            # 下面一行是绝对路径传入获取配置文件的方法。
            return curr_path[0:index_of_com] + "com/"
        else:
            # 下面一行的相对路径会随测试py文件位置而变化，仅在测试文件绝对路径中不包含com时，做默认三层情况使用。
            return "../../../"

    @staticmethod
    def generate(config_file_name):
        test_config_file_path = TestGenerator._get_com_path() + "zijie/tests/case_config/" + config_file_name
        test_config_file = open(test_config_file_path, 'r')
        str_val = test_config_file.read()
        dict_array = json.loads(str_val)
        if "rest" in config_file_name.lower() or "http" in config_file_name.lower():
            for test_dict in dict_array:
                # 每一个dict是一个测试文件。
                TestGenerator.rest_generate(
                    rest_test_file_path=test_dict['rest_test_file_path'],
                    test_class_name=test_dict['test_class_name'],
                    domain_host_url=test_dict['domain_host_url'],
                    case_info_dict_list=test_dict['case_info_dict_list']
                )
        elif "rpc" in config_file_name.lower() or "thrift" in config_file_name.lower():
            for test_dict in dict_array:
                # 每一个dict是一个测试文件。
                TestGenerator.rpc_generate(
                    thrift_test_file_path=test_dict['thrift_test_file_path'],
                    test_class_name=test_dict['test_class_name'],
                    thrift_file_name=test_dict['thrift_file_name'],
                    case_info_dict_list=test_dict['case_info_dict_list']
                )


if __name__ == "__main__":
    TestGenerator.generate("restful_case_config.json")
    TestGenerator.generate("thrift_case_config.json")

    # case_info_dict_list = [
    #     {
    #         "order": 1,
    #         "test_method_name": "test_case",
    #         "inter_name": "被测接口",
    #         "protocol_type": "HTTP",
    #         "inter_path": "/union_pangle",
    #         "http_method": "GET"
    #     },
    #     {
    #         "order": 2,
    #         "test_method_name": "test_parameter_case",
    #         "inter_name": "被测接口1",
    #         "protocol_type": "HTTP",
    #         "inter_path": "/union_pangle/parameter",
    #         "http_method": "POST",
    #         "parameters": "var, param",
    #     },
    # ]
    # TestGenerator.rest_generate(
    #     rest_test_file_path="auto_test.py",
    #     test_class_name="TestAuto",
    #     domain_host_url="https://boe-pangle-ssr.bytedance.net",
    #     case_info_dict_list=case_info_dict_list
    # )
