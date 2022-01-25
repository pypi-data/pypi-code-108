"""
description: this provides the class FactoryTestSuite.
"""
import os
import subprocess
import time
from pathlib import Path

from pistar_echo_agent.utilities.constants import TEST_CASE
from pistar_echo_agent.utilities.constants import FAIL_REASON
from .directory import Directory


class FactoryTestSuite:
    """
    description: this class is used to manage the testsuite sent by cloud test.
    """
    testcases_information = None
    logger = None
    stop = None
    __execute_testcase = None
    __execute_mode = None
    __exception_count = None
    exception_timeout = None
    exception_pause = None
    exception_stop = None
    exception_install = None
    fail_reason = None
    process = None

    def __init__(
            self,
            testcases_information,
            script_root_path,
            logger,
            execute_mode,
            report_path
    ):
        self.logger = logger
        self.testcases_information = testcases_information
        self.script_root_path = script_root_path
        self.report_path = str(report_path)
        self.__execute_mode = execute_mode
        self.stop = False
        self.__exception_count = 0

    def execute(self):
        """
        description: this function is used to execute the testsuite.
        """
        if self.install_requirements() is False:
            return
        # 根据用例类型执行用例
        for testcase_type in self.testcases_information:
            if self.stop:
                self.logger.info("Stop flag is true, now stop the process.")
                return
            testcases = self.testcases_information[testcase_type]
            # 判断是否弹出异常
            is_execute_success = self.__execute_testcases(testcases, testcase_type)
            while is_execute_success is False:
                self.__exception_count += 1
                # 如果异常超过3次，直接退出，不再继续执行
                if self.__exception_count > 2:
                    self.exception_stop = True
                    self.logger.info("Exception pause exceeds 3 times, now stop current task.")
                    return

                # 轮询异常暂停标志位，是否可以继续执行
                while self.exception_pause:
                    time.sleep(0.1)
                if len(testcases) == 0:
                    break
                self.logger.info("Exception pause resume, continue execute unfinished test cases.")
                is_execute_success = self.__execute_testcases(testcases, testcase_type)

    def install_requirements(self):
        require_path = Path(self.script_root_path).joinpath("requirements.txt")
        if not require_path.exists():
            self.logger.warning("There is no requirements in the project.")
            return True
        command = ["pip3", "install", "-r", "requirements.txt"]
        with Directory(self.script_root_path):
            try:
                subprocess.run(
                    command,
                    env=os.environ,
                    check=True,
                    encoding="utf8",
                    timeout=100,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
            except subprocess.TimeoutExpired:
                self.logger.error("pip install run timeout.")
                self.exception_install = True
                self.fail_reason = FAIL_REASON.INSTALL_TIMEOUT
                return False
            except subprocess.CalledProcessError as exc:
                self.logger.error(f"pip install error.\n {exc.stderr}")
                self.exception_install = True
                self.fail_reason = f"{FAIL_REASON.INSTALL_ERROR}\n{exc.stderr}"
                return False
        self.logger.info("pip install success.")
        return True

    def __execute_testcases(self, testcases, testcase_type):
        command = self.get_testcase_execution_command(testcases, testcase_type)
        with Directory(self.script_root_path):
            self.process = subprocess.Popen(
                command,
                env=os.environ,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Set process timeout 2 hour temporarily.
            try:
                self.process.communicate(timeout=7200)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.logger.error("Test cases execute timeout.")
                # Set the timeout flag and set test cases result is timeout.
                self.exception_timeout = True
                return True

            if self.stop is True:
                return True
            if self.process.returncode != 0:
                self.logger.warning("Test cases execute have some exceptions, now set exception pause.")
                self.exception_pause = True
                return False
        self.logger.info("{} test cases execute completed.".format("pistar"))
        return True

    def get_testcase_execution_command(self, testcases, testcase_type):
        command = ["pistar", "run"]
        for testcase in testcases:
            command.append(testcase[TEST_CASE.ABS_PATH])
        if testcase_type == TEST_CASE.PYTEST:
            command += ['--type', 'pytest']
        command += ['-o', self.report_path]
        command += ['--debug']
        # 之后加上用例的超时时间
        self.logger.info("Current command is: {}".format(command))
        return command

    def kill_process(self):
        if self.process:
            self.process.kill()
