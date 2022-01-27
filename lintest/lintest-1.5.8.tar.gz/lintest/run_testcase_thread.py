import threading
import traceback

from .base_testcase import BaseTestCase


class StartTestcaseThread(threading.Thread):
    """
    StartTestcaseThread is used to call the testcase's runTest()/run_test() method,
    and will set the testcases's done_flag as "True" after execution done without any exception.

    @author: Wang Lin
    """

    def __init__(self, executing_testcase):
        threading.Thread.__init__(self)
        self.executing_testcase = executing_testcase

    def run(self):
        # 先执行 setup()， 再执行 run_test()

        try:
            # 执行 setup() 之前 先 log TestEngineCaseInput(如果是 test-engine 发起的)
            if BaseTestCase.TestEngineCaseInput:
                self.executing_testcase.logger.info("------ TestEngineCaseInput:")
                self.executing_testcase.logger.info(self.executing_testcase.TestEngineCaseInput)

            if hasattr(self.executing_testcase, "setup"):
                self.executing_testcase.logger.info("------ execute setup() Start")
                self.executing_testcase.setup()
                self.executing_testcase.logger.info("------ execute setup() End")
        except BaseException:
            traceback.print_exc()
            pass

        try:
            if hasattr(self.executing_testcase, "runTest"):
                print("the method runTest() is deprecated, please re-name it as run_test()")
                self.executing_testcase.logger.info("================== runTest() start:")
                self.executing_testcase.runTest()
            else:
                self.executing_testcase.logger.info("================== run_test() start:")
                self.executing_testcase.run_test()
        except BaseException:
            traceback.print_exc()
            self.executing_testcase.exception_info = traceback.format_exc()
        else:
            self.executing_testcase.done_flag = True
