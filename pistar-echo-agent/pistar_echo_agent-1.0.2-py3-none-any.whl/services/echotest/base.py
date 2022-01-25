import copy
import json
import os
import shutil
import threading
import time
from pathlib import Path

import yaml

from pistar_echo_agent.resources.loggers import server_logger
from pistar_echo_agent.utilities.configuration.server_configuration import server_configuration
from pistar_echo_agent.utilities.constants import ENCODE
from pistar_echo_agent.utilities.constants import ENVIRONMENT
from pistar_echo_agent.utilities.constants import FAIL_REASON
from pistar_echo_agent.utilities.constants import FILE_MODE
from pistar_echo_agent.utilities.constants import FILE_NAME
from pistar_echo_agent.utilities.constants import LOG_PATH
from pistar_echo_agent.utilities.constants import RESPONSE
from pistar_echo_agent.utilities.constants import STATUS_CODE
from pistar_echo_agent.utilities.constants import TEST_CASE
from pistar_echo_agent.utilities.constants import TEST_SUITE
from pistar_echo_agent.utilities.testcase import compose_exception_report
from pistar_echo_agent.utilities.testcase import compose_report_json
from pistar_echo_agent.utilities.testsuite import FactoryTestSuite
from pistar_echo_agent.utilities.util import get_convert_path
from pistar_echo_agent.utilities.util import get_current_time_format
from pistar_echo_agent.utilities.util import get_current_timestamp
from pistar_echo_agent.utilities.util import get_fail_response
from pistar_echo_agent.utilities.util import sha256
from pistar_echo_agent.utilities.util import trace_exception


class EchoTestTask:
    port = None
    __testsuite = None
    __is_running = False
    # 存储已经完成的用例
    __testcases_done = None
    # 存储用例报告
    __testcases_report = None
    # 根据用例类型信息存储不同的用例
    __testcases_type = None
    # 根据用例类型存储未完成的用例
    __unfinished_testcases_type = None
    # 用例块的信息
    __current_task_info = None
    __checked_flag = True
    __execute_flag = True
    __env_content = None
    report_path = None

    def __init__(self):
        self.lock = threading.RLock()

    def heartbeat(self, request_id):
        if self.__current_task_info:
            server_logger.info(f"Current task block_id is: {self.__current_task_info[TEST_SUITE.BLOCK_ID]}")
        else:
            server_logger.info("No task is being executed.")
        server_logger.info("Receive heartbeat info. " + request_id)
        return STATUS_CODE.OK, {RESPONSE.TIMESTAMP: get_current_timestamp()}

    def send_testcases(self, task_info, testcases):
        is_submit_thread = False
        if self.__is_running:
            is_submit_success = False
        else:
            self.lock.acquire()
            try:
                if self.__is_running:
                    is_submit_success = False
                else:
                    self.__init_variable()
                    self.__current_task_info = copy.deepcopy(task_info)
                    is_submit_thread = self.execute(testcases)
                    is_submit_success = True
                    self.__is_running = True
            finally:
                self.lock.release()

        if is_submit_success is False:
            server_logger.error(FAIL_REASON.SUBMIT_RUNNING)
            return get_fail_response(STATUS_CODE.BAD_REQUEST, FAIL_REASON.SUBMIT_RUNNING)

        if is_submit_thread is True:
            pistar_log_path = Path(task_info[TEST_SUITE.TESTCASE_ROOT_PATH]).joinpath(LOG_PATH.PISTAR)
            server_logger.info("Start test suite successfully, begin to execute test cases.")
            return STATUS_CODE.OK, {RESPONSE.BLOCK_ID: self.__current_task_info[TEST_SUITE.BLOCK_ID],
                                    RESPONSE.TASK_START: get_current_timestamp(),
                                    RESPONSE.LOG_PATHS: [str(pistar_log_path), server_logger.output_path]}
        else:
            server_logger.error(FAIL_REASON.SUBMIT_EXCEPTION)
            self.__is_running = False
            return get_fail_response(STATUS_CODE.INTERNAL_SERVER_ERROR, FAIL_REASON.SUBMIT_EXCEPTION)

    def execute(self, testcases):
        try:
            self.__set_report_path()
            self.__deal_testcases(testcases)
            self.__deal_environment_param()

            # If the task has no valid case, the task will not be executed.
            if not self.__unfinished_testcases_type:
                server_logger.warning("The task has no valid case, please check.")
                return True
            thread_execute = threading.Thread(target=self.execute_thread)
            thread_execute.daemon = True
            thread_execute.start()
            # 开启检查用例状态的线程
            thread_check_status = threading.Thread(target=self.check_testcase_status)
            thread_check_status.daemon = True
            thread_check_status.start()
            return True
        except BaseException as exception:
            trace_exception(exception, server_logger)
            return False

    def __init_variable(self):
        self.__testcases_report = {}
        self.__testcases_type = {}
        self.__unfinished_testcases_type = {}
        self.__testcases_done = []
        self.__env_content = {ENVIRONMENT.TEST_CASE_ENV: {}}

    def __convert_repeated_testcases(self, testcases):
        """
        convert repeated test cases file path to new copy file path
        """
        if not Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]).exists():
            server_logger.error("Internal error: the project root path is not exists, please check.")
            for testcase in testcases:
                testcase[TEST_CASE.IS_VALID] = False
                testcase[TEST_CASE.SCRIPT_PATH] = ""
                self.__set_abnormal_file(testcase, FAIL_REASON.PROJECT_PATH_NOT_EXISTS)
            return
        unique_file_paths = set()
        repeated_file_paths = set()
        # check which test cases have duplicate script files.
        for testcase in testcases:
            if self.__check_key_valid(testcase) is False:
                continue
            testcase[TEST_CASE.SCRIPT_PATH] = testcase[TEST_CASE.SCRIPT_PATH].strip()
            file_path = Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]) \
                .joinpath(testcase[TEST_CASE.SCRIPT_PATH])
            # check whether test case file path is valid.
            if self.__check_file_path(file_path, testcase) is False:
                testcase[TEST_CASE.IS_VALID] = False
            else:
                testcase[TEST_CASE.IS_VALID] = True
                if str(file_path) in unique_file_paths:
                    repeated_file_paths.add(str(file_path))
                else:
                    unique_file_paths.add(str(file_path))
        if len(repeated_file_paths) == 0:
            return None
        self._set_new_script_path(repeated_file_paths, testcases)

    def _set_new_script_path(self, repeated_file_paths, testcases):
        """
        traverse test cases, copy the renaming of repeated test cases, and set new script path.
        """
        for testcase in testcases:
            if testcase[TEST_CASE.IS_VALID] is False:
                continue
            file_path = Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]) \
                .joinpath(testcase[TEST_CASE.SCRIPT_PATH])
            if str(file_path) in repeated_file_paths:
                new_script_path = get_convert_path(testcase[TEST_CASE.SCRIPT_PATH], testcase[TEST_CASE.NAME])
                new_file_path = Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]).joinpath(new_script_path)
                shutil.copy(file_path, new_file_path)
                server_logger.info(f"copy repeated file {file_path} to {new_file_path}.")
                testcase[TEST_CASE.SCRIPT_PATH] = new_script_path

    def __deal_testcases(self, testcases):
        """
        construct the test cases struct, and deal environment param
        """
        self.__convert_repeated_testcases(testcases)
        server_logger.info("================Test case info====================")
        for testcase in testcases:
            if testcase[TEST_CASE.IS_VALID] is False:
                continue
            file_path = str(Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH])
                            .joinpath(testcase[TEST_CASE.SCRIPT_PATH]))
            testcase[TEST_CASE.ABS_PATH] = file_path
            # set environment yaml key: value is script path: test case name
            testcase_script_path = str(Path(testcase[TEST_CASE.SCRIPT_PATH]))
            self.__env_content[ENVIRONMENT.TEST_CASE_ENV][testcase_script_path] = testcase[TEST_CASE.NAME]
            # set test case report path with sha256
            testcase_report_path = self.report_path.joinpath(sha256(file_path))
            testcase[TEST_CASE.REPORT_PATH] = str(testcase_report_path)
            # set test case to execute list
            self.__set_testcase_type(testcase, self.__current_task_info[TEST_SUITE.TYPE])
        server_logger.info("================Test case info====================")

    def __check_key_valid(self, testcase):
        """
        check script_path is in test case data
        """
        if TEST_CASE.SCRIPT_PATH not in testcase:
            testcase[TEST_CASE.IS_VALID] = False
            testcase[TEST_CASE.SCRIPT_PATH] = ""
            server_logger.error(f"The '{testcase[TEST_CASE.NAME]}' script_path key is not exists.")
            self.__set_abnormal_file(testcase, FAIL_REASON.SCRIPT_PATH_IS_EMPTY)
            return False
        return True

    def __check_file_path(self, file_path, testcase):
        if testcase[TEST_CASE.SCRIPT_PATH] == "":
            server_logger.error(f"The '{testcase[TEST_CASE.NAME]}' script_path value is empty.")
            self.__set_abnormal_file(testcase, FAIL_REASON.SCRIPT_PATH_IS_EMPTY)
            return False
        if not file_path.exists():
            server_logger.error(f"The '{testcase[TEST_CASE.NAME]}' test case not exist, "
                                f"the absolute path is {file_path}.")
            self.__set_abnormal_file(testcase, FAIL_REASON.FILE_NOT_EXISTS)
            return False
        if not file_path.is_file():
            server_logger.error(f"The '{testcase[TEST_CASE.NAME]}' script path is not a file, "
                                f"the absolute path is {file_path}.")
            self.__set_abnormal_file(testcase, FAIL_REASON.PATH_NOT_FILE)
            return False
        if not str(file_path).endswith(".py"):
            server_logger.error(f"The '{testcase[TEST_CASE.NAME]}' script path is not a python file, "
                                f"the absolute path is {file_path}.")
            self.__set_abnormal_file(testcase, FAIL_REASON.WRONG_FILE_FORMAT)
            return False
        return True

    def __set_testcase_type(self, testcase, test_type):
        cases = self.__testcases_type.get(test_type, [])
        cases.append(testcase)
        self.__testcases_type[test_type] = cases
        unfinished_cases = self.__unfinished_testcases_type.get(test_type, [])
        unfinished_cases.append(testcase)
        self.__unfinished_testcases_type[test_type] = unfinished_cases
        server_logger.info(f'{TEST_CASE.TYPE_NAME[test_type]} test case : '
                           f'{testcase[TEST_CASE.ID]}: {testcase[TEST_CASE.NAME]} '
                           f'path is: {testcase[TEST_CASE.ABS_PATH]}')

    def __set_report_path(self):
        """
        create report dir
        """
        # TASK_NAME is external value, use Path.resolve() to delete "../" symbol, and avoid to jump current folder
        task_name = Path(self.__current_task_info[TEST_SUITE.TASK_NAME]).resolve().name
        report_folder = f"{task_name}_{self.__current_task_info[TEST_SUITE.BLOCK_ID]}_{get_current_time_format()}"
        self.report_path = server_configuration.report_path.joinpath(report_folder)
        self.report_path.mkdir(parents=True, exist_ok=True)
        server_logger.info(f"Set report path success, the report path is: {self.report_path}.")

    def __set_abnormal_file(self, testcase, reason):
        """
        Construct an exception report and write it to the test case report.
        """
        self.__testcases_report[testcase[TEST_CASE.ID]] = \
            compose_exception_report(
                self.__current_task_info,
                testcase[TEST_CASE.ID],
                testcase[TEST_CASE.SCRIPT_PATH],
                reason
            )
        self.__testcases_done.append(testcase[TEST_CASE.ID])

    def execute_thread(self):
        self.__execute_flag = False
        # 根据执行模式执行用例
        self.__testsuite = FactoryTestSuite(
            testcases_information=self.__unfinished_testcases_type,
            logger=server_logger,
            report_path=self.report_path,
            script_root_path=self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH],
            execute_mode=self.__current_task_info[TEST_SUITE.EXECUTE_MODE]
        )
        self.__testsuite.execute()
        self.__execute_flag = True

    def check_testcase_status(self):
        self.__checked_flag = False
        for testcase_type in self.__unfinished_testcases_type:
            testcases = self.__testcases_type[testcase_type]
            unfinised_testcase = self.__unfinished_testcases_type[testcase_type]
            while len(unfinised_testcase) > 0:
                # testcases is used for looping to prevent index overflow when unfinished_testcase is used for looping.
                for testcase in testcases:
                    # after stop is set, process exit
                    if self.__testsuite.stop:
                        server_logger.info("Receive stop signal. Check status thread now stop.")
                        self.__checked_flag = True
                        return
                    if not self.__is_unfinished_testcase(testcase[TEST_CASE.ID], testcase_type):
                        continue
                    self.__deal_testcase_report(testcase, testcase_type)
                # 暂定500ms的间隔，因为八爪鱼框架是3s轮询，这边可以不用那么快
                time.sleep(0.5)
        self.__checked_flag = True
        server_logger.info("Get all test cases status.")

    def __deal_environment_param(self):
        if Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]).exists():
            env_param_config = self.__current_task_info[TEST_SUITE.ENVIRONMENT_PARAMS]
            # if env param exists, parse and write it to yaml
            if env_param_config:
                for env_param in env_param_config:
                    self.__env_content[env_param[ENVIRONMENT.NAME]] = env_param
            environment_path = Path(self.__current_task_info[TEST_SUITE.TESTCASE_ROOT_PATH]).joinpath(ENVIRONMENT.PATH)
            with environment_path.open(mode=FILE_MODE.WRITE, encoding=ENCODE.UTF8) as yaml_file:
                yaml.dump(self.__env_content, yaml_file)
        else:
            server_logger.error("Internal error: the project root path is not exists, please check.")

    def __is_unfinished_testcase(self, testcase_id, testcase_type):
        for testcase in self.__unfinished_testcases_type[testcase_type]:
            if testcase_id == testcase[TEST_CASE.ID]:
                return True
        return False

    def __deal_testcase_report(self, testcase, testcase_type):
        unfinished_testcases = self.__unfinished_testcases_type[testcase_type]
        finished_file = os.path.join(testcase[TEST_CASE.REPORT_PATH], FILE_NAME.FINISHED)
        # 处理任务超时和pip安装失败以及异常的用例，直接标记失败
        if self.__deal_fail_test_cases(testcase, testcase_type):
            return
        # 异常暂停位一旦到了，首先寻找异常用例是哪个，将这个异常用例组装报告，然后将异常暂停位重置，然后退出
        if self.__testsuite.exception_pause:
            # 找到异常用例是哪个
            exception_testcase = self.__find_exception_testcase(unfinished_testcases)
            # 保证这边发生异常的时候，这边处理完成，那边才可以开始新的子进程执行用例·
            self.__testcases_report[exception_testcase[TEST_CASE.ID]] = compose_exception_report(
                self.__current_task_info,
                exception_testcase[TEST_CASE.ID],
                exception_testcase[TEST_CASE.SCRIPT_PATH],
                FAIL_REASON.RUN_EXCEPTION
            )
            self.__deal_finished_testcase(exception_testcase, testcase_type)
            self.__testsuite.exception_pause = False
        if os.path.exists(finished_file):
            # 先组合用例的报告，然后再将用例完成放入
            self.__testcases_report[testcase[TEST_CASE.ID]] = compose_report_json(
                self.__current_task_info,
                testcase[TEST_CASE.ID],
                testcase[TEST_CASE.SCRIPT_PATH],
                testcase[TEST_CASE.REPORT_PATH]
            )
            self.__deal_finished_testcase(testcase, testcase_type)

    def __deal_fail_test_cases(self, testcase, testcase_type):
        if self.__testsuite.exception_install:
            self.__testcases_report[testcase[TEST_CASE.ID]] = compose_exception_report(
                self.__current_task_info,
                testcase[TEST_CASE.ID],
                testcase[TEST_CASE.SCRIPT_PATH],
                FAIL_REASON.EXECUTOR_EXCEPTION
            )
            self.__deal_finished_testcase(testcase, testcase_type)
            return True
        # 如果异常停止标志位，不再轮询用例的finished文件，直接返回所有的用例
        if self.__testsuite.exception_stop:
            self.__testcases_report[testcase[TEST_CASE.ID]] = compose_exception_report(
                self.__current_task_info,
                testcase[TEST_CASE.ID],
                testcase[TEST_CASE.SCRIPT_PATH],
                FAIL_REASON.EXECUTOR_EXCEPTION
            )
            self.__deal_finished_testcase(testcase, testcase_type)
            return True
        # 添加任务超时的处理逻辑
        if self.__testsuite.exception_timeout:
            self.__testcases_report[testcase[TEST_CASE.ID]] = compose_exception_report(
                self.__current_task_info,
                testcase[TEST_CASE.ID],
                testcase[TEST_CASE.SCRIPT_PATH],
                FAIL_REASON.TIMEOUT_EXCEPTION
            )
            self.__deal_finished_testcase(testcase, testcase_type)
            return True
        return False

    def __find_exception_testcase(self, testcases):
        cur_path = self.report_path.joinpath(FILE_NAME.CUR_TASK)
        if not cur_path.exists():
            server_logger.error(f"The exception meta info {cur_path} cannot find.")
            return testcases[0]

        try:
            with cur_path.open(mode=FILE_MODE.READ, encoding=ENCODE.UTF8) as json_file:
                content = json.load(json_file)
        except Exception as ex:
            server_logger.error(ex)
            server_logger.error(f"{cur_path} json file have some error, please check.")
            return testcases[0]

        cur_script = content["cur_script"]
        cur_script_path = str(Path(cur_script))
        for testcase in testcases:
            if testcase[TEST_CASE.ABS_PATH] == cur_script_path:
                server_logger.info(f"The test case {cur_script_path} is exception test case.")
                return testcase
        exception_testcase_path = testcases[0][TEST_CASE.SCRIPT_PATH]
        server_logger.error(f"Cannot find exception test case {cur_script}, "
                            f"now set {exception_testcase_path} test case is exception.")
        return testcases[0]

    def __deal_finished_testcase(self, testcase, testcase_type):
        self.__testcases_done.append(testcase[TEST_CASE.ID])
        server_logger.info(
            f"Test case {testcase[TEST_CASE.NAME]} : {testcase[TEST_CASE.ID]} has been executed."
        )
        self.__unfinished_testcases_type[testcase_type].remove(testcase)

    def clean(self, block_id):
        if not self.check_request_valid(block_id):
            return get_fail_response(STATUS_CODE.BAD_REQUEST, FAIL_REASON.BLOCK_ID_ERROR)
        self.__clean_logs()
        self.__testsuite = None
        self.__is_running = False
        self.__testcases_done = None
        self.__testcases_report = None
        self.__testcases_type = None
        self.__current_task_info = None
        self.report_path = None
        self.__unfinished_testcases_type = None
        self.__execute_flag = True
        self.__checked_flag = True
        server_logger.info(f"Block {block_id} clean environment successfully.")

        return STATUS_CODE.OK, {RESPONSE.TIMESTAMP: get_current_timestamp()}

    def __clean_logs(self):
        # clean agent log
        agent_log_path = server_logger.output_path
        with open(agent_log_path, FILE_MODE.WRITE, encoding=ENCODE.UTF8) as out:
            out.write("")

        # clean result folder report_path
        try:
            if self.report_path.exists():
                shutil.rmtree(self.report_path)
        except OSError as e:
            server_logger.error(f"Delete pistar result temp files path {self.report_path} fail, Error:{e.strerror}")

    def stop(self, block_id):
        if self.__current_task_info:
            if not self.check_request_valid(block_id):
                return get_fail_response(STATUS_CODE.BAD_REQUEST, FAIL_REASON.BLOCK_ID_ERROR)
            if self.__testsuite:
                server_logger.info("Now begin to kill the process.")
                self.__testsuite.stop = True
                self.__testsuite.kill_process()
                server_logger.info("kill success.")
            while True:
                # 确保两个线程都退出了，返回stop结束
                if self.__checked_flag and self.__execute_flag:
                    break
                time.sleep(0.1)
        else:
            server_logger.warning("No task is executed.")

        return STATUS_CODE.OK, {RESPONSE.BLOCK_ID: block_id, RESPONSE.TASK_END: get_current_timestamp()}

    def get_task_status(self, block_id):
        if not self.check_request_valid(block_id):
            return get_fail_response(STATUS_CODE.BAD_REQUEST, FAIL_REASON.BLOCK_ID_ERROR)
        response = []
        if len(self.__testcases_done) > 0:
            server_logger.info(f"Completed test cases are {self.__testcases_done}.")
            for tid in self.__testcases_done:
                response.append({TEST_CASE.ID: tid, RESPONSE.IS_EXECUTED: True})
        return STATUS_CODE.OK, response

    def get_task_report(self, block_id, testcase_ids):
        if not self.check_request_valid(block_id):
            return get_fail_response(STATUS_CODE.BAD_REQUEST, FAIL_REASON.BLOCK_ID_ERROR)
        # 组合用例报告
        report = []
        for testcase_id in testcase_ids:
            if testcase_id not in self.__testcases_report:
                continue
            report.append(json.dumps(self.__testcases_report[testcase_id]))
        return STATUS_CODE.OK, report

    def check_request_valid(self, block_id):
        if not self.__current_task_info:
            server_logger.error(f"Error block_id:'{block_id}', no task is being executed.")
            return False
        if block_id != self.__current_task_info[TEST_SUITE.BLOCK_ID]:
            server_logger.error(f"Error block_id, the block_id:'{block_id}' is not current block_id.")
            return False
        return True
