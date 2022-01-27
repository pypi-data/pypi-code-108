import logging
import time
import traceback
# import threading

from .logged_requests import LoggedRequests
from pprint import pformat
from pprint import pprint


try:
    import settings
except ImportError:
    traceback.print_exc()

class BaseTestCase(object):
    """
BaseTestCase is the superclass for all the backend(Non UI) and frontend(UI) Testcases and Mobile Testcases
@author: Wang Lin
"""

    # TestEngineCaseInput 即 TestEngineCaseInput from github action（ test-engine目前只支持单线程）
    TestEngineCaseInput = {}

    # GlobalData 是全局数据对象（各个不同的thread发起的不同的testase直接共享该数据）
    GlobalData = {}

    priority = None

    def __init__(self):
        self.pprint = pprint
        self.pformat = pformat
        self.logger = logging
        self.requests = LoggedRequests

        self.testcase_id = None

        self.TestEngineCaseInput = BaseTestCase.TestEngineCaseInput

        # TestEngineTestEngineCaseOutput: case由test-engine触发执行结束后call-back时传入的参数（ test-engine目前只支持单线程）
        self.TestEngineCaseOutput = {}

        self.GlobalData = BaseTestCase.GlobalData

        # # todo: 此处用于 构建多线程时 每个线程独立的 TestEngineCaseInput(线程id作为key)
        # print("===================+++++++++++++==========threading.currentThread().ident")
        # print(threading.currentThread().ident)

        # self.CaseData 用于记录 case执行过程中产生的数据（多数情况用于 某个 testcase chain中, 某个Testcase中有调用了 另外一个Testcase.run_test() 则此case 被定义一个 TestcaseChain）
        # eg:
        # from lintest.api_testcase import APITestCase
        # from tests.api.testcase_demo.testcase1 import Testcase1
        # from tests.api.testcase_demo.testcase2 import Testcase2
        #
        # class Testcase3(APITestCase):
        #     tag = 'case3'
        #
        #     def run_test(self):
        #         # 如下调用方式 Testcase1 & Testcase2 的log 不会 被保存到 Testcase3 的log 中
        #         # Testcase1().run_test()
        #         # Testcase2().run_test()
        #         # print(self.CaseData)
        #
        #         # 如下调用方式 Testcase1 & Testcase2 的log  会  被保存到 Testcase3 的log 中
        #
        #         # 比如： TestAdd1.run_test(self)中会设置 username, self.CaseData['username'] = 'lin'
        #         Testcase1.run_test(self)
        #
        #         # TestAdd2.run_test(self)中会设置 password, self.CaseData['password'] = res['password'], 其中 res可能是某个方法或方法的返回值
        #         Testcase2.run_test(self)
        #
        #         # 此时可以在 TestAdd3 直接通过 self.CaseData 获取 对应的 username & password
        #         self.logger.info(self.CaseData)
        #         self.logger.info(self.CaseData['username'])
        #         self.logger.info(self.CaseData['password'])
        #
        #         # login(self.CaseData['username']), self.CaseData['password']))
        self.CaseData = {}

    # now timeout only support integer seconds, default value is 1200 seconds
    timeout = getattr(settings, "TESTCASE_TIMEOUT", 1200)

    def sleep(self, sleep_seconds):
        time.sleep(sleep_seconds)

    def run_test(self):
        """
        this method must be implement by all backend test cases,
        each test case must encapsulate its business logic into a specific method which called run_test():
        def run_test(self):
            ...
        """
        raise NotImplementedError("---subclass: %s must implement this method: run_test(self)!" % self)

    def teardown(self):
        """
        def teardown(self):
            ...
        """
        pass

    def setup(self):
        """
        def teardown(self):
            ...
        """
        pass

    # def tearDown(self):
    #     """
    #     def teardown(self):
    #         ...
    #     """
    #     pass

    # def get_testcase_id(self):
    #     return self.testcase_id

    # @abc.abstractmethod
    # def set_testcase_id(self):
    #     """
    #     self.testcase_id = "real testcase_id"
    #     """
    #     pass

    # # todo: really need this?
    # def set_testcase_id(self):
    #     set_testcase_id_msg = """
    #     Note: you should add set_testcase_id() in your testcase like below:
    #     def set_testcase_id():
    #         testcase_id = "1"
    #     """
    #     framework_logger.error(set_testcase_id_msg)

    def assert_equals(self, actual_val, expect_val):
        try:
            assert actual_val == expect_val
            self.logger.info("assert actual_val: %s == expect_val: %s  ====== Passed" % (actual_val, expect_val))
        except AssertionError as e:
            e.args += ('expected value is %s' % expect_val, 'actual_val is %s' % actual_val)
            self.logger.info("assert_equals(%s, %s)  ------ Failed" % (actual_val, expect_val))
            raise

    def assert_is_not_none(self, actual_val):
        try:
            assert actual_val is not None
            self.logger.info("assert %s is not None  ====== Passed" % (actual_val))
        except AssertionError as e:
            e.args += ('expected value is not None', 'actual_val is %s' % actual_val)
            self.logger.info("assert_is_not_none(%s)  -- Failed" % (actual_val))
            raise
