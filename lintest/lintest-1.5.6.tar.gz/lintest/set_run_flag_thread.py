import threading


class SetRunFlagThread(threading.Thread):
    """
    class SetRunFlagThread is used to set the executing_test_case's run_flag to "True"
    @author: Wang Lin
    """

    def __init__(self, executing_test_case):
        threading.Thread.__init__(self)
        self.executing_test_case = executing_test_case

    def run(self):
        self.executing_test_case.run_flag = True
