"""
Utility classes to use with pytest unit tests and mocked methods
"""

MOCK_ERROR_MESSAGE = 'Mocked exception was raised'


# pylint: disable=too-few-public-methods
class MockCalledMethod:
    """
    Class to mock a method or function and check it's call arguments

    Monkeypatch instance of this class to the place and store call variables
    """
    def __init__(self, return_value=None):
        self.call_count = 0
        self.args = []
        self.kwargs = []
        self.return_value = return_value

    def __call__(self, *args, **kwargs):
        """
        Increment call count, store method arguments and return stored value
        """
        self.call_count += 1
        self.args.append(args)
        self.kwargs.append(kwargs)
        return self.return_value


# pylint: disable=too-few-public-methods
class MockReturnTrue(MockCalledMethod):
    """
    Mock a method to always return True
    """
    def __init__(self):
        super().__init__(return_value=True)


# pylint: disable=too-few-public-methods
class MockReturnFalse(MockCalledMethod):
    """
    Mock a method to always return False
    """
    def __init__(self):
        super().__init__(return_value=False)


# pylint: disable=too-few-public-methods
class MockReturnEmptyList(MockCalledMethod):
    """
    Mock a method to always return None
    """
    def __init__(self):
        super().__init__(return_value=[])


class MockCheckOutput(MockCalledMethod):
    """
    Mock calling subprocess.check_output and returning data read from a file instead
    """
    def __init__(self, path, encoding='utf-8'):
        super().__init__()
        self.path = path
        self.encoding = encoding

    def __call__(self, *args, **kwargs):
        """
        Call mocked check_output, storing call argument and returning data from self.path file
        """
        super().__call__(*args, **kwargs)
        with open(self.path, encoding=self.encoding) as handle:
            return bytes(handle.read(), encoding=self.encoding)


class MockRunCommandLineOutput(MockCalledMethod):
    """
    Mock calling sys_toolkit.subprocess.run_command_lineoutput and returning data
    read from a file instead
    """
    def __init__(self, path=None, encoding='utf-8', stdout=None, stderr=None):
        super().__init__()
        self.path = path
        self.encoding = encoding
        self.stdout = stdout if stdout else []
        self.stderr = stderr if stderr else ''

    def __call__(self, *args, **kwargs):
        """
        Call mocked check_output, storing call argument and returning data from self.path file
        """
        super().__call__(*args, **kwargs)
        if self.path is not None:
            with open(self.path, encoding=self.encoding) as handle:
                return handle.read().splitlines(), self.stderr
        return self.stdout, self.stderr


# pylint: disable=too-few-public-methods
class MockException(MockCalledMethod):
    """
    Mock raising specified exception when method is called. Stores call arguments just like
    MockCalledMethod before raising the exception

    Custom arguments to the raised exception can be passed with *args and **kwargs. If no
    arguments are passed exception and default_message is True, exception is raised with
    string MOCK_ERROR_MESSAGE, otherwise it's raised with on arguments
    """
    def __init__(self, exception=Exception, default_message=True, **exception_kwargs):
        super().__init__()
        self.exception = exception
        self.default_message = default_message
        self.exception_kwargs = exception_kwargs if exception_kwargs else {}

    def __call__(self, *args, **kwargs):
        """
        Store call arguments and raise specified exception with specified arguments
        or mocked message if nothing was specified
        """
        super().__call__(*args, **kwargs)
        print('raise exception', self.exception)
        if self.exception_kwargs:
            raise self.exception(**self.exception_kwargs)
        if self.default_message:
            raise self.exception(MOCK_ERROR_MESSAGE)
        raise self.exception
