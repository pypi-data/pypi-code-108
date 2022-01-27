class UserspaceHandlerException(Exception):
    def __init__(self, exception_source, exception_trigger, exception):
        self.exception_source = exception_source
        self.exception_trigger = exception_trigger
        self.exception = exception
        super(UserspaceHandlerException, self).__init__('user unhandled exception in roxx expression')
        