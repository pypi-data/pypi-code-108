class TestCaseTimeoutException(Exception):
    def __init__(self, message):
        super(TestCaseTimeoutException, self).__init__(message)
