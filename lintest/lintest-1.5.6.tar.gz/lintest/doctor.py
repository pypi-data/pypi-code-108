"""
This module is used to:
 1. check the necessary settings files for lintest Automation Framework
 2. analysis the testcases then give the execute suggestions

@author: Wang Lin
"""
import os
import sys
import importlib
import traceback
import platform

from .get_ios_devices_list import get_ios_device_list
from .get_project_info import get_project_info


project_info = get_project_info()

# SETTINGS_INIT_STRING is used to define the default settings/__init__.py content. if there are no settings/__init__.py found
# in the project. then framework will auto generate settings/__init__.py
SETTINGS_INIT_STRING = """
# settings/__init__.py is used to configure below items for the lintest Automation Framework
#  1. FRAMEWORK_LOGGER_LEVEL & TESTCASE_LOGGER_LEVEL
#  2. Environment (test environment: UAT, QA, LIVE ...)
#  3. TESTCASE_TIMEOUT (After Testcase_Timeout seconds, if the testcase still running then throw TimeoutException)
#  4. RERUN_FLAG (control rerun failed testcases. Default is False)
#  5. DEBUG_RUN (if debug test cases locally then keep the browser active after execution done. Default value is False)
#  6. QUEUE_SIZE (set queue_size as 8 means that there are at most 8 test cases can be executed concurrently)
#  7. implicitly_wait which only used for webdriver(browser)
#  8. Configuration for Mobile Test ( update follow your business)
#  9. APPIUM_SERVER_DEFAULT_IP = "127.0.0.1"
#  10.APPIUM_SERVER_DEFAULT_PORT = 4723
#  11.IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST
#  12.ios_desired_capabilities
#  13.ios_implicitly_wait
#  14.android_apk_path
#  15.customized_android_capabilities
#  16.android_implicitly_wait
#  17.DEVICE_ID_NAME_DICT
#  18.ANDROID_TESTCASE_ACCOUNT
#  19.# SaveScreenshotForPassedTestCaseFlag
#  20. Configuration for Browser option ( update follow your business)

import logging

FRAMEWORK_LOGGER_LEVEL = logging.INFO
TESTCASE_LOGGER_LEVEL = logging.DEBUG


class Environment(object):
    UAT = "uat"
    QA = "qa"
    LIVE = "www"

ENVIRONMENT = Environment.UAT
# ENVIRONMENT = Environment.QA
# ENVIRONMENT = Environment.LIVE

# set Test Case Timeout as 1200 seconds
TESTCASE_TIMEOUT = 1200

# control rerun function, default is True
RERUN_FLAG = True

# if debug test cases locally then keep the browser active after execution done. Default value is False
DEBUG_RUN = False

# set queue_size as 8 means that there are at most 8 test cases can be executed concurrently
QUEUE_SIZE = 8

# SaveScreenshotForPassedTestCaseFlag default value if False
SaveScreenshotForPassedTestCaseFlag = False

# set the webdriver's implicitly_wait default value: 60
implicitly_wait = 60

# configure for Database
if ENVIRONMENT == Environment.UAT:
    DATABASE = {
        "Server": "uat-server",
        "User": "uat-user",
        "Password": "uat-password"
    }

if ENVIRONMENT == Environment.QA:
    DATABASE = {
        "Server": "qa-server",
        "User": "qa-user",
        "Password": "qa-password"
    }

if ENVIRONMENT == Environment.LIVE:
    DATABASE = {
        "Server": "live-server",
        "User": "live-user",
        "Password": "live-password"
    }


# ---------------------- config for mobile test --------------------------
APPIUM_SERVER_DEFAULT_IP = "127.0.0.1"
APPIUM_SERVER_DEFAULT_PORT = 4723

# -------- set IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST --------
# IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST is used to control the priority of ios_desired_capabilities which
# maybe provided in settings and testcase, default value is False.
# 1. if IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST = True
#    then the ios_desired_capabilities in settings will override in testcase.
# 2. if IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST = False
#     or no IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST found in settings
#   then will use the ios_desired_capabilities which provided in testcase.
# 3. if there are only one ios_desired_capabilities provided by settings or testcase,
#    then just use it whatever IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST is True or False.
# 4. if no ios_desired_capabilities provided by both settings and testcase then raise exception
IOS_DESIRED_CAPABILITIES_IN_SETTINGS_FIRST = False

# if there are no ios_desired_capabilities found from testcase, then use below as default
from lintest.ios_testcase import IOSTestCase

# -------- set ios_desired_capabilities --------
ios_desired_capabilities = {
    'app': 'app/lintest.app',  # required, "app" directory must under your project, or provide the absolute path
    # 'platformName': 'iOS', # if not provide, will be auto set by lintest framework
    # 'platformVersion': '10.2', # if not provide, will be auto set by lintest framework
    'deviceName': IOSTestCase.DeviceNameList.iPhone6,  # or 'deviceName': 'iPhone 6'
    # 'udid': 'xxx', # for real device
}

# set the implicitly wait time for ios driver, default value is 60 (in seconds)
ios_implicitly_wait = 60

# -------- set android_apk_path --------
android_apk_path = "here should be the real app path.apk"

# set the implicitly wait time for android driver, default value is 60 (in seconds)
android_implicitly_wait = 60

# here can add the customized android capabilities, eg: 'newCommandTimeout: 300'
customized_android_capabilities = "'newCommandTimeout': 300"

# map the device_name with device_id
DEVICE_ID_NAME_DICT = {
    "device_id1": "device_name1",
    "device_id2": "device_name2",
}

# set the android test account, map the user_name & password
ANDROID_TESTCASE_ACCOUNT = {
    "username1": "password1",
    "username2": "password2",
}

# ---------------------- config for browser option --------------------------
# browser option must be a string list, e.g: BROWSER_OPTION = ["--headless", "--window-size=1280x1024"]
BROWSER_OPTION = []


# ---------------------- config for android option --------------------------
# android option must be a string list, e.g: ANDORID_OPTION = ["--chromedriver-path", "the real chromedriver path"]
ANDORID_OPTION = []

"""

# TESTCASE_TAGS_STRING is used to define the class Tags in testcase_tags.py as a reference.
TESTCASE_TAGS_STRING = """# encoding: utf-8
# define the Tags Class for testcases

class Tags(object):
    '''
    class Tags is used to define all the testcase's tags.
    set the tag for each testcase (tag can be any non-blank string, you can identify it follow your business.
        eg."smoke", "nightly", "ignore", also can be the author "Lin")
        Note: # if one testcase's tag contains "ignore", then it will only be added into ignore_testcase_list, even its
            tag attribute contains other tag name

    there are two ways to set tag for testcase
        1. set tag attribute as a string (each tag name split by "," )
        2. recommend: set tag attribute as a list(each tag name define in this Tags class.)

    class FrontendTestcaseDemo(UITestCase):
        # set tag by way 1, this testcase will be auto added into smoke_testcase_list and nightly_testcase_list
        tag = "smoke, nightly"

        # set tag by way 2(recommend this way), it's easy to know all the tag names in your project and will not type
        # an error tag name, eg. type "nighty" as "nightly")
        # this testcase will be auto added into lin_testcase_list & smoke_testcase_list & todo_testcase_lit
        tag = [Tags.Smoke, Tags.Todo]

        def run_test(self):
            self.logger.debug("load google")
            self.browser.get("https://www.google.com")

    Note: the tag name is Not Case Sensitive, that means tag = "smoke" same with tag = "SMOKE"

    @author: Lin Wang
    '''
    Nightly = "nightly"
    Smoke = "smoke"
    Lin = "lin"
    Ignore = "ignore"
    Todo = "todo"
"""


# auto generate settings package, write SETTINGS_INIT_STRING into settings/__init__.py
def generate_settings():
    os.mkdir(project_info.project_path + os.sep + "settings")
    with open(project_info.project_path + os.sep + "settings" + os.sep + "__init__.py", "w") as settings_init_file:
        settings_init_file.write(SETTINGS_INIT_STRING)


# auto generate class Tags
def generate_testcase_tags():
    with open(project_info.project_path + os.sep + "settings" + os.sep + "testcase_tags.py", "w") as testcase_tag_file:
        testcase_tag_file.write(TESTCASE_TAGS_STRING)


def generate_ios_device_list():
    ios_device_list = get_ios_device_list()
    ios_device_str_list = []
    for device_name in ios_device_list:
        ios_device_str_list.append(device_name.replace(" ", "").replace("(", "").replace(")", "").replace(".", "_").replace("-", "_") + ' = ' + '"' + device_name + '"')

    str = ""
    for device_name_str in ios_device_str_list:
        str  += "    " + device_name_str + "\n"

    IOS_DEVICE_LIST_STRING = """
class IOSDeviceNameList:
%s""" % str

    with open(project_info.project_path + os.sep + "settings" + os.sep + "ios_device_list.py", "w") as ios_device_list:
        ios_device_list.write(IOS_DEVICE_LIST_STRING)


def execute_suggestion(testcase_dict=None):
    """
    after doctor check, Doctor will give the execute suggestions.

    """
    print("""-------- there are 5 ways to execute testcase:
1. run CMD: "python run.py tag_name" (here provide the tag_name, then will execute all the testcase which
           has been set tag as tag_name)
 or
2. run CMD: "python run.py TestCaseClassName" (here provide the testcase's class_name: TestCaseClassName(case-insensitive),
           then will execute testcase TestCaseClassName)
 or
3. run CMD: "python run.py testcase_list_name" (provide the testcase_list_name which is defined in each package's
                                    __init__.py file)
 or
4. run CMD: "python run.py package_name" (provide the package_name such as: tests.backend  or tests or
                                    tests.backend.b1)
 or
5. run CMD: "python run.py tag1 tag2 testcase_list_1 testcase_list_2 TestcaseClassName1 package_name_1" (the parameters
                for run.py can be any combination of the following 4 kinds which separated by a space:
                    1. tag_name  (e.g: "smoke" or "regression"
                    2. testcase's class_name (e.g: "TestBackendB1_1")
                    3. testcase_list_name  (e.g: "tests_backend_testcases")
                    4. package_name (e.g: "tests" or "tests.backend" or "tests.frontend")
                all the testcases which fetched by the given parameters will be added into testcase_list, and will do
                data deduplication for testcase_list.
                for each parameters:
                    first try to find it as a tag name, if no tag name found then try to find it as a TestcaseClassName,
                    if no TestcaseClassName found, then try to find it as a TestcaseList, if no TestcaseList found, then
                    try to find it as a package_name
""")

    if testcase_dict is None:
        from .auto_generate_testcase_list import auto_generate_testcase_list
        testcase_dict = auto_generate_testcase_list(call_by_doctor=True)

    if len(testcase_dict.keys()) == 0:
        print("------ there are no tag name found from all the testcases!\n")
    else:
        print("------ found below tag name from your project:")
        print(testcase_dict.keys())
        print(
            "\n------ the testcase list which group by tag name are under: " + project_info.project_path + os.sep + "tests" + os.sep + "tag_testcases")
        print(
            "\n------ run CMD: 'python main.py --help' to see the Usage() for lintest Automation Test Framework ------\n")


def doctor_check():
    """
        doctor_check is used to check the necessary settings files for lintest Automation Framework.
        will auto generate them if not found.
        1. check settings/__init__.py exists
        2. check settings/testcase_tags.py exists
        3. check class Tags exists in settings/testcase_tags.py
    """

    # 1. check whether your_project/settings/__init__.py exists, auto generate it if not
    if not os.path.exists(project_info.project_path + os.sep + "settings" + os.sep + "__init__.py"):
        print("there are no settings package found in your project")
        generate_settings()
        print(
            "auto generate settings/__init__.py done, you should update related configurations by your business logic")
    print("1. check settings/__init__.py exists done")

    # 2. check whether module your_project/settings/testcase_tags.py exists, auto generate it if not exists
    if not os.path.exists(project_info.project_path + os.sep + "settings" + os.sep + "testcase_tags.py"):
        generate_testcase_tags()
    print("2. check settings/testcase_tags.py exists done")

    # 3. check whether class Tags exists in your_project/settings/testcase_tags.py
    try:
        # if there are no testcase_tags found from project, doctor will auto generate it.
        from settings.testcase_tags import Tags
    except ImportError:
        traceback.print_exc()
        print(
            "Warning: there are no Tags found from your_project" + os.sep + "settings" + os.sep + "testcase_tags.py")
        generate_testcase_tags()
        # print type(sys.modules['settings.testcase_tags'])  # output: <type 'module'>

        # module settings.testcase_tags has been added into sys.modules(sys.modules act as the modules cache) when
        # execute "from settings.testcase_tags import Tags", it means that at the begin even there are no Tags defined
        # in settings.testcase_tags.py but the module settings.testcase_tags still be cached in sys.modules. so here
        # must reload() the module "settings.testcase_tags"
        importlib.reload(sys.modules['settings.testcase_tags'])  # reload() require a module as argument

        # module settings.testcase_tags has been added into sys.modules(sys.modules act as the modules cache) when
        # execute "from settings.testcase_tags import Tags", it means that at the begin even there are no Tags defined
        # in settings.testcase_tags.py but the module settings.testcase_tags still be cached in sys.modules.
        # so here execute exec "from settings.testcase_tags import Tags" still use the cached module(still no Tags
        # defined in module settings.testcase_tags without reload it)
        # exec "from settings.testcase_tags import Tags" # this line not work, must call reload()

        print("Auto generate settings" + os.sep + "testcase_tags.py  done!")
        print(
            "Warning: the file testcase_tags which was auto generated just for reference, you should update the tag" \
            " name follow your business logic!\n")
    print("3. check class Tags exists in settings/testcase_tags.py\n")


def doctor():
    """
    doctor() is used to check the necessary configuration files and auto generate them if not exists.
    will give the execution suggestion after check().
    """
    doctor_check()

    from .auto_generate_testcase_list_from_csv import auto_generate_testcase_list_from_csv
    auto_generate_testcase_list_from_csv()

    from .auto_generate_testcase_list import auto_generate_testcase_list

    testcase_dict_for_tags, testcase_dict_for_classname, testcase_dict_for_package = auto_generate_testcase_list(call_by_doctor=True)

    execute_suggestion(testcase_dict_for_tags)

    # auto generate ios_device_name_list.py if on Mac OS
    if platform.system() == "Darwin":
        pass
        # generate_ios_device_list() # 暂时注释掉，目前先不开启 appium

    # try:
    #     # below codes should be executed after check the configuration files done. if below codes executed at the begin
    #     # of doctor(), will throw exception when there are no Tags found from settings/testcase_tags.py(because
    #     # some testcases maybe reference the the tag name which defined in class Tags)
    #     from .auto_generate_testcase_list import auto_generate_testcase_list
    #
    #     testcase_dict_for_tags, testcase_dict_for_classname, testcase_dict_for_package = auto_generate_testcase_list()
    #
    #     execute_suggestion(testcase_dict_for_tags)
    # except BaseException:
    #     traceback.print_exc()


if __name__ == "__main__":
    doctor()
