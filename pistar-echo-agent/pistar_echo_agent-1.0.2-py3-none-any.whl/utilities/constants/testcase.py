"""
description: this module provides the constant TEST_CASE.
"""
from enum import Enum


class TEST_CASE:
    """
    description: the test case attributes.
    """

    ID = 'id'
    NAME = 'name'
    TYPE = 'testcase_type'
    SCRIPT_PATH = 'script_path'
    PYTEST = '7'
    PISTAR = '6'
    ABS_PATH = 'absolute_path'
    REPORT_PATH = 'report_path'
    TYPE_NAME = {'6': 'pistar', '7': 'pytest'}
    TYPE_LIST = ['6', '7']
    IS_VALID = "is_valid"


class TEST_SUITE:
    BLOCK_ID = "block_id"
    TASK_ID = "task_id"
    SUB_TASK_ID = "sub_task_id"
    TASK_NAME = "task_name"
    EXECUTE_MODE = "execute_mode"
    TESTCASE_ROOT_PATH = "testcase_root_path"
    TYPE = "testcase_type"
    EXTEND_CONTENT = "extend_content"
    TESTCASES = "testcases"
    ENVIRONMENT_PARAMS = "env_param_config"
    SERIAL_MODE = "1"
    PARALLEL_MODE = "2"


class FAIL_REASON:
    """
    description: the test case fail reason.
    """
    SUBMIT_RUNNING = "Submit fail, there is a task in progress."
    SUBMIT_EXCEPTION = "Submit fail, there is some exceptions in progress."
    BLOCK_ID_ERROR = "The request block_id is not equals current task."
    SCRIPT_PATH_IS_EMPTY = "脚本路径字段未填写."
    PROJECT_PATH_NOT_EXISTS = "内部错误：仓库目录不存在."
    FILE_NOT_EXISTS = "脚本用例文件不存在."
    PATH_NOT_FILE = "脚本路径不是文件."
    RUN_EXCEPTION = "执行用例发生异常退出."
    EXECUTOR_EXCEPTION = "执行机异常超过3次, 用例停止执行."
    TIMEOUT_EXCEPTION = "任务执行超时."
    WRONG_FILE_FORMAT = "脚本用例文件不是python文件."
    INSTALL_TIMEOUT = "pip安装依赖环境超时."
    INSTALL_ERROR = "pip安装依赖出错."
    INTERNAL_EXCEPTION = "执行器内部出错，请联系维护人员."


class ENVIRONMENT:
    PATH = "environment.yaml"
    TEST_CASE_ENV = "env_testcase"
    NAME = "name"


class Result(Enum):
    PASSED = 1
    FAILED = 2
    TIMEOUT = 3
    ERROR = 4
    BROKEN = 5
    SKIPPED = 6
    UNKNOWN = 7
