import threading
import time


class TimeoutThread(threading.Thread):
    """
    class TimeoutThread is used to control the timeout for testcase execution.
    will set executing_test_case's timeout_flag as "True" after timeout.

    @author: Wang Lin
    """

    def __init__(self, executing_test_case):
        threading.Thread.__init__(self)
        self.executing_test_case = executing_test_case

    def run(self):
        # here sleep 0.1 second to make sure the run_testcase_thread.StartTestcaseThread(executing_testcase) executed,
        # because the testcase can set its own timeout.  eg: self.timeout = 100
        time.sleep(0.1)
        # print(self.executing_test_case.timeout)
        time.sleep(self.executing_test_case.timeout)
        self.executing_test_case.timeout_flag = True
