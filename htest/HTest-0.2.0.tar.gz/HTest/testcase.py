#!/usr/bin/env python3.7
# encoding: utf-8
# 测试用例解析

import io
import json
import os
import sys
import yaml
import exception
from HTest import write_yaml, clear_yaml
from HTest.logger import logger

sys.path.append(os.path.dirname(__file__))
case_lists = {}


def _load_yaml_file(yaml_file):
    """ load yaml file and check file content format
    """
    with io.open(yaml_file, 'r', encoding='utf-8') as stream:
        yaml_content = yaml.load(stream, Loader=yaml.FullLoader)
        check_format(yaml_file, yaml_content)
        return yaml_content


def _load_json_file(json_file):
    """ load json file and check file content format
    """
    with io.open(json_file, encoding='utf-8') as data_file:
        try:
            json_content = json.load(data_file)
        except exception.JSONDecodeError:
            err_msg = u"JSONDecodeError: JSON file format error: {}".format(json_file)
            logger.error(err_msg)
            raise exception.FileFormatError(err_msg)

        check_format(json_file, json_content)
        return json_content


def _load_csv_file(csv_file):
    """ load csv file and check file content format
    @param
        csv_file: csv file path
        e.g. csv file content:
            username,password
            test1,111111
            test2,222222
            test3,333333
    @return
        list of parameter, each parameter is in dict format
        e.g.
        [
            {'username': 'test1', 'password': '111111'},
            {'username': 'test2', 'password': '222222'},
            {'username': 'test3', 'password': '333333'}
        ]
    """
    csv_content_list = []
    parameter_list = None
    collum_num = 0
    with io.open(csv_file, encoding='utf-8') as data_file:
        for line in data_file:
            line_data = line.strip().split(",")
            if line_data == [""]:
                # ignore empty line
                continue

            if not parameter_list:
                # first line will always be parameter name
                parameter_list = line_data
                collum_num = len(parameter_list)
                continue

            # from the second line
            if len(line_data) != collum_num:
                err_msg = "CSV file collum does match with headers.\n"
                err_msg += "\tcsv file path: {}\n".format(csv_file)
                err_msg += "\terror line content: {}".format(line_data)
                raise exception.FileFormatError(err_msg)
            else:
                csv_data = {}
                for index, parameter_name in enumerate(parameter_list):
                    csv_data[parameter_name] = line_data[index]

                csv_content_list.append(csv_data)

    return csv_content_list


def load_file(file_path):
    if not os.path.isfile(file_path):
        logger.error("Testcase file does not exist")
        exit(0)

    file_suffix = os.path.splitext(file_path)[1].lower()
    if file_suffix == '.json':
        return _load_json_file(file_path)
    elif file_suffix in ['.yaml', '.yml']:
        return _load_yaml_file(file_path)
    elif file_suffix == ".csv":
        return _load_csv_file(file_path)
    else:
        err_msg = u"Unsupported file format"
        logger.warning(err_msg)
        return []


def check_format(file1, content):
    """ check testcase format if valid
    """
    if not content:
        # testcase file content is empty
        err_msg = u"Testcase file content is empty"
        logger.error(err_msg)
        exit(0)

    elif not isinstance(content, (list, dict)):
        # testcase file content does not match testcase format
        err_msg = u"Testcase file is not dict or list"
        logger.error(err_msg)
        exit(0)


def load_test_file(file):
    """ load test file, get test data structure.
    @param file: absolute valid test file path
    @return test data
        {
            "step-list": [function, path, pathname, args],
            "case-list": [step1, step2…………],
            "main-list": [case1, case2…………]
        }
    """
    tests_list = load_file(file)
    if "step-list" in tests_list:
        # logger.debug("Testcase file is test step")
        data_step = tests_list.get("step-list")
        return data_step

    elif "case-list" in tests_list:
        # logger.debug("Testcase file is test case")
        data_case = tests_list.get("case-list")
        return data_case

    elif "main-list" in tests_list:
        # logger.debug("Testcase file is test suite")
        data_suit = tests_list.get("main-list")
        return data_suit

    else:
        logger.error("Testcase file content format invalid")
        exit(0)


def load_folder_files(folder_path, recursive=True):
    """ load folder path, return all files in list format.
    @param
        folder_path: specified folder path to load
        recursive: if True, will load files recursively
    """
    if isinstance(folder_path, (list, set)):
        files = []
        for path in set(folder_path):
            files.extend(load_folder_files(path, recursive))

        return files

    if not os.path.exists(folder_path):
        return []

    file_list = []

    for dirpath, dirnames, filenames in os.walk(folder_path):
        filenames_list = []

        for filename in filenames:
            if not filename.endswith(('.yml', '.yaml', '.json')):
                continue
            filenames_list.append(filename)

        for filename in filenames_list:
            filepath = os.path.join(dirpath, filename)
            file_list.append(filepath)

        if not recursive:
            break

    return file_list


test_def_overall_dict = {
    "case": {},
    "suit": {}
}


def load_folder_dependencies():
    """
    load all suit definitions.
    default suite folder is "$CWD/testcase/suit".
    default case folder is "$CWD/testcase/case".
    """
    global case_lists
    suite_folder = os.path.join(os.getcwd(), "testcase", "suit")
    suite_files = load_folder_files(suite_folder)
    for suite_file in suite_files:
        suite = load_test_file(suite_file)
        test_def_overall_dict["suit"].update(suite)
        case_name = suite.get("import")
        case_file = os.path.join(case_name + ".yml")
        case_folder = os.path.join(os.getcwd(), "testcase", "case")
        case_files = load_folder_files(case_folder)
        if case_file in case_files:
            case_lists = load_test_file(case_file)
            test_def_overall_dict["case"].update(case_lists)
        else:
            logger.warning("{} does not exist, please make the case file first".format(case_file))
        return case_lists


class Get_data:
    """ load test file, get test data structure.
    @param path: absolute valid test file path
    @return test data
    """

    def __init__(self, path):
        self.path = path

    def get_main_list(self):
        data_suit = load_test_file(self.path)
        return data_suit

    def get_url(self):
        test_list = load_file(self.path)
        for item in test_list:
            if item == "url":
                url = test_list.get("url")
                return url

    def get_case_list(self):
        test_list = load_file(self.path)
        for item in test_list:
            if item == "import":
                case_name = test_list.get("import")
                case = os.path.join(case_name + ".yml")
                case_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(self.path))), 'case')
                case_files = load_folder_files(case_folder)
                for case_file in case_files:
                    file = case_file.split("/")[-1]
                    if str(file) == str(case):
                        case_data_dependencies = load_test_file(case_file)
                        return case_data_dependencies

    def get_project_path(self):
        project_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(self.path)))))
        return project_path


def get_data(file_paths):
    main_list = Get_data(file_paths).get_main_list()
    case_list = Get_data(file_paths).get_case_list()
    url = Get_data(file_paths).get_url()
    BASE_DIR = Get_data(file_paths).get_project_path()
    clear_yaml()
    write_yaml({'url': url, 'case-list': case_list, 'main-list': main_list, 'BASE_DIR': BASE_DIR})


if __name__ == '__main__':
    get_data("/home/hangshu/taolei/ui自动化框架/HS-V0.0.2/Project/testcase/suit/login-suit.yml")
