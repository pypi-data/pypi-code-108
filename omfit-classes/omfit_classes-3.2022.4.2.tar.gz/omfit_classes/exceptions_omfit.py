import sys
import signal
import traceback


def print_last_exception(file=sys.__stderr__):
    """
    This function prints the last exception that has occurred
    """
    print('', file=file)
    print('--------------------', file=file)
    etype, value, tb = sys.exc_info()
    excpStack = traceback.format_exception(etype, value, tb)
    print(''.join(excpStack), file=file)


def print_stack():
    return traceback.print_stack(file=sys.__stderr__)


# ---------------------
# OMFIT exceptions
# ---------------------
class doNotReportException(object):
    """
    Exceptions that inherit from this class will not trigger
    an email sent be set to the OMFIT developer team
    """

    pass


class EndOMFITpython(KeyboardInterrupt, doNotReportException):
    """
    Class used to stop the running python script
    without reporting it to the OMFIT developer team
    """

    def __init__(self, message='', *args, **kw):
        KeyboardInterrupt.__init__(self, message, *args, **kw)
        if isinstance(message, str) and len(message):
            print(message, file=sys.stderr)


class EndAllOMFITpython(KeyboardInterrupt, doNotReportException):
    """
    Class used to stop the entire python workflow
    without reporting it to the OMFIT developer team
    """

    def __init__(self, message='', *args, **kw):
        KeyboardInterrupt.__init__(self, message, *args, **kw)
        if isinstance(message, str) and len(message):
            print(message, file=sys.stderr)


class OMFITexception(Exception, doNotReportException):
    """
    Class used to raise an exception in a user's script
    without reporting it to the OMFIT developer team
    """

    def __init__(self, message='', *args, **kw):
        Exception.__init__(self, message, *args, **kw)


class ReturnCodeException(RuntimeError):
    """
    Class used to raise an exception when a code return code is !=0
    """

    pass


def signalHandler(signal=None, frame=None):
    raise EndAllOMFITpython('\n\n---> Aborted by user <---\n\n')


try:
    signal.signal(signal.SIGTERM, signalHandler)
except ValueError:
    # ValueError: signal only works in main thread
    pass

__all__ = [
    'print_last_exception',
    'print_stack',
    'doNotReportException',
    'EndOMFITpython',
    'EndAllOMFITpython',
    'OMFITexception',
    'ReturnCodeException',
    'signalHandler',
]
