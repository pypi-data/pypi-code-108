import unittest

from rox.core.error_handling.userspace_unhandled_error_invoker import UserspaceUnhandledErrorArgs, UserspaceUnhandledErrorInvoker
from rox.core.error_handling.exception_trigger import ExceptionTrigger
from rox.core.logging.logging import Logging

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

# A test error handler - was using the mock, but for some reason the UserspaceUnhandledErrorArgs arg doesn't seem to be
# retrievable properly when running CI.
class TestHandler:
    call_count = 0
    lastArg = None

    def handleError(self, arg):
        self.call_count += 1
        self.lastArg = arg


class UserspaceUnhandledErrorInvokerTests(unittest.TestCase):

    def test_will_pass_error_to_handler(self):
        user_unhandled_error_invoker = UserspaceUnhandledErrorInvoker()

        handler = TestHandler()
        user_unhandled_error_invoker.set_handler(handler.handleError)

        exception_source = '123'
        exception_trigger = ExceptionTrigger.CONFIGURATION_FETCHED_HANDLER
        exception = Exception('something went wrong')
        user_unhandled_error_invoker.invoke(exception_source, exception_trigger, exception)

        self.assertEqual(1, handler.call_count)
        self.assertIsInstance(handler.lastArg, UserspaceUnhandledErrorArgs)
        self.assertEqual(exception_source, handler.lastArg.exception_source)
        self.assertEqual(exception_trigger, handler.lastArg.exception_trigger)
        self.assertEqual(exception, handler.lastArg.exception)

    def test_will_write_error_when_invoke_user_userhandled_error_invoked_handler_wasnt_set(self):
        user_unhandled_error_invoker = UserspaceUnhandledErrorInvoker()
        obj = '123'

        log = Mock()
        Logging.set_logger(log)

        user_unhandled_error_invoker.invoke(obj, ExceptionTrigger.CONFIGURATION_FETCHED_HANDLER, Exception('some exception'))
        
        self.assertEqual(1, len(log.error.call_args_list))
        args, _ = log.error.call_args_list[0]
        self.assertTrue('User Unhandled Error Occurred' in args[0])

    def test_will_write_error_when_involer_user_unhandled_error_invoker_threw_exception(self):
        user_unhandled_error_invoker = UserspaceUnhandledErrorInvoker()
        obj = '123'

        log = Mock()
        Logging.set_logger(log)

        def raise_(ex):
            raise ex
        handler = lambda args: raise_(Exception('userUnhandlerErrorException'))
        user_unhandled_error_invoker.set_handler(handler)
        user_unhandled_error_invoker.invoke(obj, ExceptionTrigger.CONFIGURATION_FETCHED_HANDLER, Exception('theOriginalException'))

        self.assertEqual(1, len(log.error.call_args_list))
        args, _ = log.error.call_args_list[0]
        self.assertTrue('User Unhandled Error Handler itself' in args[0])
        # Check the message contains details of both the original, and the handler exceptions:
        self.assertTrue('userUnhandlerErrorException' in args[0])
        self.assertTrue('theOriginalException' in args[0])
