"""
This module is used to:
 1. generate the testcase list in init.py files under tests package according what testcases the package include
 2. generate the testcase list by tag names under settings/tag_testcases

Created on Aug. 5, 2018

@author: Wang Lin
"""

import os
import time
import shutil
import sys
import traceback
import py_compile

try:
    import settings
except ImportError:
    traceback.print_exc()

import importlib

from collections import OrderedDict
from . import get_project_info
from . import android_testcase
from .get_adb_devices import get_adb_devices
from .clean_data import clear_init_file, remove_android_temp
from .doctor import doctor_check
from .android_testcase import AndroidTestCase
from .base_testcase import BaseTestCase

from .memory_usage import log_memory_usage

ANDROID_TESTCASE_PACKAGE_NAME = "android"
ANDROID_TESTCASE_TEMP_PACKAGE_NAME = "android_temp"
REAL_DEVICE = android_testcase.AndroidTestCase.REAL_DEVICE
VIRTUAL_DEVICE = android_testcase.AndroidTestCase.VIRTUAL_DEVICE
APPIUM_SERVER_PORT = int(getattr(settings, 'APPIUM_SERVER_DEFAULT_PORT', 4723))

PROJECT_INFO = get_project_info.get_project_info()
TESTS_PACKAGE_PATH = PROJECT_INFO.project_path + os.sep + PROJECT_INFO.testcase_package_name
ANDROID_TEMP_PACKAGE_PATH = TESTS_PACKAGE_PATH + os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME
TAG_TESTCASES_DIRECTORY = TESTS_PACKAGE_PATH + os.sep + PROJECT_INFO.tag_testcase_package_name

remove_android_temp(ANDROID_TESTCASE_TEMP_PACKAGE_NAME)
clear_init_file()

try:
    exec("from tests.ignore_testcases_list import IgnoreTestCases")
except BaseException:
    print("\nWARNING: No IgnoreTestcases list found from your project\n")

    # if the IgnoreTestCases doesn't exists. here define a new list to store all the testcases which has "ignore"
    # tag, will ignore these "ignored" testcases when auto generate the testcases list in __init__.py files .
    IgnoreTestCases = []


def generate_testcase_list(testcase_dict):
    if os.path.exists(TAG_TESTCASES_DIRECTORY):
        shutil.rmtree(TAG_TESTCASES_DIRECTORY)

    os.mkdir(TAG_TESTCASES_DIRECTORY)
    open(TAG_TESTCASES_DIRECTORY + os.sep + "__init__.py", "w")

    for key in testcase_dict.keys():
        values = testcase_dict.get(key)

        with open(TAG_TESTCASES_DIRECTORY + os.sep + key + ".py", "w") as file_obj:

            if key == "ignore":

                for value in values:
                    file_obj.write("from %s import %s\n" % (value.__module__, value.__name__))

                file_obj.write("\n%s_testcase_list = [%s" % (key, "\n"))

                for value in values:
                    file_obj.write("    " + value.__name__ + ",")
                    file_obj.write("\n")

            else:
                file_obj.write("import tests")
                file_obj.write("\n")
                file_obj.write("\n")

                file_obj.write("%s_testcase_list = [%s" % (key, "\n"))

                for value in values:
                    file_obj.write("    " + value.__module__ + "." + value.__name__ + ",")
                    file_obj.write("\n")

            file_obj.write("]")


def get_class_name_list_from_module(file_full_name, testcase_dict_for_tags, testcase_dict):
    file_full_name = PROJECT_INFO.project_path + os.sep + file_full_name
    import_string_list = []
    class_name_list = []
    contains_run_test = False
    contains_tag_flag = False

    with open(file_full_name, "r", encoding='utf-8') as file_object:
        # if there are no "tag" found in the file content, then will not add this testcase into testcase_dict_for_tags
        for line in file_object:
            if line.replace(" ", "").__contains__("tag="):
                contains_tag_flag = True
                break

    with open(file_full_name, "r", encoding='utf-8') as file_object:
        # if there are no run_test() or runTest() method found in the file content, then this file not a TestCase file
        for line in file_object:
            if line.__contains__("def ") and (
                        line.__contains__("run_test(") or line.__contains__("runTest(")) and line.__contains__(":") \
                    and not line.strip().startswith("#"):
                contains_run_test = True
                break

    if contains_run_test is True:
        with open(file_full_name, "r", encoding='utf-8') as file_object:

            for line in file_object:
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_string_list.append(line.strip())

                if line.startswith("class ") and line.__contains__("(") and line.__contains__(":") and \
                        not line.strip().startswith("#"):
                    class_name_string, base_class_name_string = line.split("(")
                    base_class_name_string_list = base_class_name_string.split(")")[0].strip().split(",")
                    class_name = class_name_string.split(" ")[-1]
                    import_base_class_flag = False
                    import_base_class_index = 0

                    for import_string in import_string_list:
                        for base_class_name_string in base_class_name_string_list:
                            if import_string.__contains__(base_class_name_string):
                                exec(import_string)
                                import_base_class_index += 1
                                break

                        if import_base_class_index == len(base_class_name_string_list):
                            import_base_class_flag = True
                            break

                    if import_base_class_flag is False:
                        break

                    namespace = {}
                    exec(import_string,namespace)  # this line must be exits(TestcaseA extends from CheckoutTestcase which is subclass of FrontendTestCase
                    exec("base_class_name = %s" % base_class_name_string, namespace)
                    base_class_name = namespace['base_class_name']

                    # if base_class_name is not the subclass of BaseTestCase, then this class is not a TestCase Class
                    if not issubclass(base_class_name, BaseTestCase):
                        break

                    module_path_str = file_full_name.split(PROJECT_INFO.project_path)[1]
                    module_path_str = module_path_str.replace(os.sep, ".")
                    module_path_str = module_path_str.replace(".tests.", "tests.")
                    module_path_str = module_path_str.strip()
                    module_path_str = module_path_str[:-3]

                    module_import_str = "from %s import %s" % (module_path_str, class_name)
                    exec(module_import_str, namespace)

                    testcase = None
                    exec("testcase = %s" % class_name, namespace)
                    testcase = namespace['testcase']
                    ignore_flag = False

                    if hasattr(testcase, "tag") and (contains_tag_flag is True):
                        if "ignore" not in testcase.tag:
                            testcase_dict[class_name.lower()] = testcase
                    else:
                        testcase_dict[class_name.lower()] = testcase

                    if hasattr(testcase, "tag") and (contains_tag_flag is True):
                        if isinstance(testcase.tag, str):
                            tags = testcase.tag.lower().split(",")
                            if class_name.__contains__(REAL_DEVICE) and issubclass(testcase, AndroidTestCase):
                                tags.append(class_name.split(REAL_DEVICE)[0].lower())
                            elif class_name.__contains__(VIRTUAL_DEVICE) and issubclass(testcase, AndroidTestCase):
                                tags.append(class_name.split(VIRTUAL_DEVICE)[0].lower())

                            tags = [tag.replace(".", "_") for tag in tags]

                            if "ignore" in [tag.strip() for tag in tags]:
                                ignore_flag = True
                            else:
                                for tag in tags:
                                    if tag.strip() in testcase_dict_for_tags.keys():
                                        testcase_dict_for_tags[tag.strip()].append(testcase)
                                    else:
                                        testcase_dict_for_tags[tag.strip()] = []
                                        testcase_dict_for_tags[tag.strip()].append(testcase)

                        elif isinstance(testcase.tag, list):
                            if "ignore" in [tag.lower().strip() for tag in testcase.tag]:
                                ignore_flag = True
                            else:
                                tags = [tag.replace(".", "_").lower() for tag in testcase.tag]

                                for tag in tags:
                                    if tag.strip() in testcase_dict_for_tags.keys():
                                        testcase_dict_for_tags[tag.strip()].append(testcase)
                                    else:
                                        testcase_dict_for_tags[tag.strip()] = []
                                        testcase_dict_for_tags[tag.strip()].append(testcase)

                    if ignore_flag is True:
                        IgnoreTestCases.append(module_import_str)
                        IgnoreTestCases.append(class_name)

                        if "ignore" in testcase_dict_for_tags.keys():
                            testcase_dict_for_tags["ignore"].append(testcase)
                        else:
                            testcase_dict_for_tags["ignore"] = []
                            testcase_dict_for_tags["ignore"].append(testcase)
                    else:
                        class_name_list.append(class_name)

    return class_name_list


def generate_andoid_testcase_temp_packages(android_testcases_package_list):
    for package_name in android_testcases_package_list:
        package_name = package_name.split(".android.")[1]
        name_list = package_name.split(".")

        new_package_path = TESTS_PACKAGE_PATH + os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME

        for name in name_list:
            new_package_path = new_package_path + os.sep + name

            if "__pycache__" in new_package_path:
                continue

            if not os.path.exists(new_package_path):
                os.mkdir(new_package_path)

                with open(new_package_path + os.sep + "__init__.py", "w"):
                    pass


def get_class_name_list(file_full_name):
    import_string_list = []
    class_name_list = []
    contains_run_test = False

    with open(file_full_name, "r", encoding='utf-8') as file_object:
        # if there are no run_test() or runTest() method found in the file content, then this file not a TestCase file
        for line in file_object:
            if line.__contains__("def ") and (
                        line.__contains__("run_test(") or line.__contains__("runTest(")) and line.__contains__(":") \
                    and not line.strip().startswith("#"):
                contains_run_test = True
                break

    if contains_run_test is True:
        with open(file_full_name, "r", encoding='utf-8') as file_object:

            for line in file_object:
                if line.strip().startswith("import ") or line.strip().startswith("from "):
                    import_string_list.append(line.strip())

                if line.startswith("class ") and line.__contains__("(") and line.__contains__(":") and \
                        not line.strip().startswith("#"):
                    class_name_string, base_class_name_string = line.split("(")
                    class_name = class_name_string.split(" ")[-1]
                    class_name_list.append(class_name)

    return class_name_list


def generate_testcase_by_device(device_name, file_full_name, file_name, directory_path, d_device_account, appium_server_port):
    user_name = d_device_account[device_name][0]
    password = d_device_account[device_name][1]

    if device_name.__contains__("."):
        device_name_for_new_testcase = "virtual_device_%s" % device_name.replace(".", "_").replace(":", "_")
    else:
        device_name_for_new_testcase = "real_device_%s" % device_name

    if directory_path.endswith(os.sep + "android"):
        new_directory_path = directory_path.replace(os.sep + "android", os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME)
    else:
        new_directory_path = directory_path.replace(os.sep + "android" + os.sep,
                                                    os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME + os.sep)

    new_testcase_file_name = file_name.split(".")[0] + "_%s" % device_name_for_new_testcase + ".py"
    new_testcase_file_full_name = new_directory_path + os.sep + new_testcase_file_name
    shutil.copyfile(file_full_name, new_testcase_file_full_name)

    with open(new_testcase_file_full_name, "r", encoding='utf-8') as new_testcase_file:
        contents = new_testcase_file.readlines()
        i = 0

        while i < len(contents):
            line = contents[i]

            if line.startswith("class ") and line.__contains__("(") and line.__contains__(":") and \
                    line.__contains__("AndroidTestCase") and not line.strip().startswith("#"):
                class_name_string, base_class_name_string = line.split("(")
                class_name = class_name_string.split(" ")[-1]
                device_name_in_class_content = device_name

                if device_name in settings.DEVICE_ID_NAME_DICT.values():
                    for key, val in settings.DEVICE_ID_NAME_DICT.items():
                        if device_name == val:
                            device_name_in_class_content = key
                            break

                if device_name.__contains__("."):
                    device_name_for_new_testcase_name = "virtual_device_%s" % device_name.replace(".", "_").replace(":",
                                                                                                                    "_")
                else:
                    device_name_for_new_testcase_name = "real_device_%s" % device_name

                # eg: 'newCommandTimeout': 120
                customized_android_capabilities = getattr(settings, "customized_android_capabilities", "")

                contents[i] = "%s\n    %s\n    %s\n" % (
                    line.replace(class_name, class_name + "_%s" % device_name_for_new_testcase_name),
                    "android_desired_capabilities = {'deviceName': '%s', 'recreateChromeDriverSessions':True, 'platformName': 'Android','unicodeKeyboard': True, 'app': '%s', %s}" % (
                        device_name_in_class_content, settings.android_apk_path, customized_android_capabilities),
                    "appium_server_port = %s" % appium_server_port
                )
            elif "USERNAME_TEMP" in line and "PASSWORD_TEMP" in line:
                contents[i] = line.replace("USERNAME_TEMP", user_name).replace("PASSWORD_TEMP", password)
            elif "self.username_temp" in line and "self.password_temp" in line:
                contents[i] = line.replace("self.username_temp", '"' + user_name + '"').replace("self.password_temp",
                                                                                                '"' + password + '"')

            # todo: how to enhance this logic ? auto set self.USERNAME_TEMP for testcase? then it can be reused in func
            # elif "USERNAME_TEMP" in line and "PASSWORD_TEMP" in line:
            #     contents[i] = line.replace("USERNAME_TEMP", user_name).replace("PASSWORD_TEMP", password)

            i += 1

        with open(new_testcase_file_full_name, "w", encoding='utf-8') as new_testcase_file:
            new_testcase_file.writelines(contents)


def auto_generate_testcase_list(call_by_doctor=False):
    log_memory_usage("start to auto_generate_testcase_list")
    test_cases_dict = {PROJECT_INFO.testcase_package_name: []}
    testcase_dict_for_tags = {}
    testcase_dict_for_classname = {}
    testcase_package_name_list = []
    testcase_dict_for_package = {}
    android_testcases_path = TESTS_PACKAGE_PATH + os.sep + "android"
    new_android_testcases_package_list = []
    device_list = []

    if call_by_doctor:
        device_list = get_adb_devices()

        if len(device_list) > 0:
            if not os.path.exists(ANDROID_TEMP_PACKAGE_PATH):
                os.mkdir(ANDROID_TEMP_PACKAGE_PATH)
                time.sleep(1)

    if os.path.exists(android_testcases_path) and (call_by_doctor is False):
        device_list = get_adb_devices()

        if len(device_list) > 0:
            if not os.path.exists(ANDROID_TEMP_PACKAGE_PATH):
                os.mkdir(ANDROID_TEMP_PACKAGE_PATH)

            android_test_account_exception_info = """
            Please make sure you provide the ANDROID_TESTCASE_ACCOUNT dict in settings file(refer below).
            For more details, please execute "python run.py --help"

            Note:
                1. the key must be the user_name and the value must be the password
                2. the number of test account must be greater than the device's count which will be run testcases concurrently
            ANDROID_TESTCASE_ACCOUNT = {
                "username_1": "password_1",
                "username_2": "password_2",
            }
            """

            if not hasattr(settings, "ANDROID_TESTCASE_ACCOUNT"):
                raise Exception(android_test_account_exception_info)

            android_test_account_dict = settings.ANDROID_TESTCASE_ACCOUNT
            android_test_account_order_dict = OrderedDict(sorted(settings.ANDROID_TESTCASE_ACCOUNT.items()))

            if len(android_test_account_dict.keys()) < len(device_list):
                not_enough_android_test_account_exception_info = """
                Error! There are no enough test account for %s devices(there are %s android devices connected),
                %s
                """ % (len(device_list), len(device_list), android_test_account_exception_info)
                raise Exception(not_enough_android_test_account_exception_info)

            android_test_account_list = [account for account in android_test_account_order_dict.items()]

            device_account_dict = {}

            for i, device in enumerate(device_list):
                device_account_dict[device] = android_test_account_list[i]

            # fetch all the test cases which in tests package and organize test cases
            for directory_path, directory_names, file_names in os.walk(android_testcases_path, topdown=True):

                for directory_name in directory_names:
                    if directory_name == "__pycache__":
                        continue
                    new_directory_path = directory_path + os.sep + directory_name
                    new_directory_path = new_directory_path.replace(PROJECT_INFO.project_path + os.sep, "")
                    new_directory_path = new_directory_path.replace(os.sep, ".")
                    new_android_testcases_package_list.append(new_directory_path)

            with open(ANDROID_TEMP_PACKAGE_PATH + os.sep + "__init__.py", "w"):
                pass

            generate_andoid_testcase_temp_packages(new_android_testcases_package_list)

            for directory_path, directory_names, file_names in os.walk(android_testcases_path, topdown=True):

                for file_name in file_names:
                    if file_name.endswith(".py") and file_name != "__init__.py":
                        file_full_name = os.path.join(directory_path, file_name)
                        class_name_list = get_class_name_list(file_full_name)

                        if len(class_name_list) > 0:

                            for device_name in device_list:
                                global APPIUM_SERVER_PORT
                                APPIUM_SERVER_PORT += 1
                                generate_testcase_by_device(device_name, file_full_name, file_name, directory_path,
                                                            device_account_dict, appium_server_port=APPIUM_SERVER_PORT)

    if os.path.exists(TAG_TESTCASES_DIRECTORY):
        shutil.rmtree(TAG_TESTCASES_DIRECTORY)

    # fetch all the test cases which in tests package and organize test cases
    for directory_path, directory_names, file_names in os.walk(TESTS_PACKAGE_PATH, topdown=True):

        for directory_name in directory_names:
            if directory_name == "__pycache__":
                continue
            new_directory_path = directory_path + os.sep + directory_name
            new_directory_path = new_directory_path.replace(PROJECT_INFO.project_path + os.sep, "")
            new_directory_path = new_directory_path.replace(os.sep, ".")

            if new_directory_path not in test_cases_dict.keys():
                test_cases_dict[new_directory_path] = []

        directory_path = directory_path.replace(PROJECT_INFO.project_path + os.sep, "")
        if directory_path == PROJECT_INFO.testcase_package_name + os.sep + "android":
            continue

        for file_name in file_names:
            file_full_name = os.path.join(directory_path, file_name)
            if file_full_name.startswith(PROJECT_INFO.testcase_package_name + os.sep + "android" + os.sep):
                continue

            if file_full_name.split(".")[-1] == "py" and file_name != "__init__.py":
                file_full_name_need_import = file_full_name.split(".py")[0]
                file_full_name_need_import = file_full_name_need_import.replace(PROJECT_INFO.project_path + os.sep, "")
                class_name_list_in_module = get_class_name_list_from_module(file_full_name, testcase_dict_for_tags,
                                                                            testcase_dict_for_classname)
                # if class_name_list_in_module is None then ignore it.
                if len(class_name_list_in_module) == 0:
                    continue

                for class_name_in_module in class_name_list_in_module:
                    need_import_string = "from %s import %s" % (
                        file_full_name_need_import.replace(os.sep, "."), class_name_in_module)

                    test_case_key = directory_path.replace(os.sep, '.')

                    if test_case_key in test_cases_dict.keys():
                        test_cases_dict[test_case_key].append(need_import_string)

                    directory_path_list = directory_path.split(os.sep)
                    directory_path_list_len = len(directory_path_list)

                    if directory_path_list_len > 1:
                        i = 1
                        key = PROJECT_INFO.testcase_package_name

                        while i < (directory_path_list_len - 1):
                            key = key + "." + directory_path_list[i]
                            test_cases_dict[key].append(need_import_string)
                            i += 1

                        test_cases_dict[PROJECT_INFO.testcase_package_name].append(need_import_string)

    # begin to generate init.py files
    for key in test_cases_dict.keys():
        values = test_cases_dict.get(key)

        init_file = PROJECT_INFO.project_path + os.sep + key.replace(".", os.sep) + os.sep + "__init__.py"

        with open(init_file, "w") as file_obj:
            class_names = []

            for value in values:
                if (value in IgnoreTestCases):
                    continue

                file_obj.write(value)
                class_names.append(value.split("import ")[-1])
                file_obj.write("\n")

            file_obj.write("\n")

            file_obj.write(key.replace(".", "_") + "_testcases = [\n")

            for class_name in class_names:
                if (class_name in IgnoreTestCases):
                    continue

                file_obj.write("    " + class_name)

                if class_names.index(class_name) < (len(class_names) - 1):
                    file_obj.write(",")
                    file_obj.write("\n")

            file_obj.write("\n]\n")

            # py_compile.compile(init_file) # todo: can i remove this line ?

    # generate testcase_list which group by tag name
    generate_testcase_list(testcase_dict_for_tags)

    for key in test_cases_dict.keys():
        if key == "tests.tag_testcases":
            continue

        testcase_package_name_list.append(key)

    for package_name in testcase_package_name_list:
        testcase_list_string = package_name.replace(".", "_") + "_testcases"

        try:
            # print("-------- start reload: ", package_name)
            # print(sys.modules)
            # because the context in the tests/xxx/__init__.py files were auto generated, here must reload the tests_xxx_testcases
            # note: must use reload, use import_module(package_name) will not work.
            importlib.reload(sys.modules[package_name])
            # importlib.import_module(package_name)
        except KeyError:
            print("Ignored file: %s" % package_name)
        else:
            try:
                exec("from %s import %s as testcase_list_for_package" % (package_name, testcase_list_string))
                exec("testcase_dict_for_package[testcase_list_string] = testcase_list_for_package")
            except BaseException:
                traceback.format_exc()

    if len(device_list) > 0 and (call_by_doctor is False):
        if "tests.android" in testcase_package_name_list:

            # "there are android testcases found, so here copy android_temp to android ..."
            for package_name in testcase_package_name_list:
                if package_name.__contains__(".android."):
                    new_package_name = package_name.replace(".android.", ".%s." % ANDROID_TESTCASE_TEMP_PACKAGE_NAME)
                    try:
                        testcase_dict_for_package[package_name.replace(".", "_") + "_testcases"] = \
                            testcase_dict_for_package[new_package_name.replace(".", "_") + "_testcases"]
                    except KeyError:
                        # KeyError means that there are no testcase found under the package_name, just ignore it
                        pass

                elif package_name == "tests.android":
                    testcase_dict_for_package["tests_android_testcases"] = testcase_dict_for_package[
                        "tests_android_temp_testcases"]

    if os.path.exists(ANDROID_TEMP_PACKAGE_PATH):
        index = 0
        android_testcase_list = []
        all_testcase_name = []
        android_temp_testcase_list = []

        with open(ANDROID_TEMP_PACKAGE_PATH + os.sep + "__init__.py", "r") as android_temp_init_file:
            android_temp_init_file_content = android_temp_init_file.readlines()

            for line in android_temp_init_file_content:
                if line.__contains__("from ") and line.__contains__(" import "):
                    line = line.split(" import ")[1].strip()
                    if line.__contains__(REAL_DEVICE):
                        class_name = line.split(REAL_DEVICE)[0]
                    elif line.__contains__(VIRTUAL_DEVICE):
                        class_name = line.split(VIRTUAL_DEVICE)[0]

                    if class_name not in all_testcase_name:
                        all_testcase_name.append(class_name)

        for class_name in all_testcase_name:
            if index < len(device_list):
                device_name = device_list[index]

                if device_name.__contains__("."):
                    device_name = device_name.replace(".", "_").replace(":", "_")
                    android_testcase_list.append(class_name + VIRTUAL_DEVICE + device_name)
                else:
                    android_testcase_list.append(class_name + REAL_DEVICE + device_name)

                index += 1
                if index == len(device_list):
                    index = 0

        # for android_testcase_name in android_testcase_list:
        #     android_temp_testcase_list.append(android_testcase_name + ",\n")
        #
        # init_file = TESTS_PACKAGE_PATH + os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME + os.sep + "__init__.py"
        # py_compile.compile(init_file)

        if call_by_doctor is False:
            for android_testcase_name in android_testcase_list:
                android_temp_testcase_list.append(android_testcase_name + ",\n")

            init_file = TESTS_PACKAGE_PATH + os.sep + ANDROID_TESTCASE_TEMP_PACKAGE_NAME + os.sep + "__init__.py"
            py_compile.compile(init_file)

            importlib.reload(sys.modules["tests.%s" % ANDROID_TESTCASE_TEMP_PACKAGE_NAME])
            exec("from tests.%s import tests_android_temp_testcases" % ANDROID_TESTCASE_TEMP_PACKAGE_NAME)
            exec("testcase_dict_for_tags['full_matrix'] = tests_android_temp_testcases")

    log_memory_usage("after execute auto_generate_testcase_list")
    return testcase_dict_for_tags, testcase_dict_for_classname, testcase_dict_for_package
#
# if __name__ == "__main__":
#     # before generate the testcase list, call doctor_check() to check the necessary configuration files.
#     doctor_check()
#
#     testcase_dict_for_tags, testcase_dict_for_classname, testcase_dict_for_package = auto_generate_testcase_list()
#
#     print("*" * 60)
#     print("the testcase list which auto organized by tag name under: %s" % TAG_TESTCASES_DIRECTORY)
#     print("*" * 60)
#
#     if len(testcase_dict_for_tags.keys()) > 0:
#         print("\n---------------------- below is the testcase list group by tag name: ----------------------")
#
#         for key in testcase_dict_for_tags.keys():
#             print("tag_name: %s," % key, " count:%s, " % len(testcase_dict_for_tags[key]), testcase_dict_for_tags[key])
#
#     if len(testcase_dict_for_classname) > 0:
#         print("\n---------------------- below is the testcase list group by class name: ----------------------")
#
#         for key, val in testcase_dict_for_classname.items():
#             print(key, ":", val)
#
#     if testcase_dict_for_package.items() > 0:
#         print("\n---------------------- below is the testcase list group by package name: ----------------------")
#
#         for key, val in testcase_dict_for_package.items():
#             print(key, ", count:%s " % len(val), val)
