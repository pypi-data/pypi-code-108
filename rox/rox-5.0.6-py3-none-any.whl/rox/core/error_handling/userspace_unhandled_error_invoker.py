from rox.core.logging.logging import Logging

class UserspaceUnhandledErrorInvoker:
    def __init__(self, user_unhandler_error_handler=None):
        self.user_unhandler_error_handler = user_unhandler_error_handler

    def invoke(self, exception_source, exception_trigger, exception):
        if not self.user_unhandler_error_handler:
            Logging.get_logger().error('User Unhandled Error Occurred, no fallback handler was set, exception ignored: {}'.format(exception))
            return
        
        try:
            self.user_unhandler_error_handler(UserspaceUnhandledErrorArgs(exception_source, exception_trigger, exception))
        except Exception as handler_exception:
            Logging.get_logger().error(
                'User Unhandled Error Handler itself threw an exception. Unhandled Error Handler exception: {}. Original exception: {}'.format(handler_exception, exception)
            )

    def set_handler(self, handler):
        self.user_unhandler_error_handler = handler


# Container object to be passed to user error handler.
# Wraps the parameters to make it easier to add new ones in the future whilst preserving backward compatibility because the function args don't change.
class UserspaceUnhandledErrorArgs:
    def __init__(self, exception_source=None, exception_trigger=None, exception=None):
        self.exception_source = exception_source
        self.exception_trigger = exception_trigger
        self.exception = exception

    def __repr__(self):
        return 'UserspaceUnhandledErrorArgs({}, {}, {})'.format(self.exception_source, self.exception_trigger, self.exception)

    def __str__(self):
        return 'UserspaceUnhandledErrorArgs({}, {}, {})'.format(self.exception_source, self.exception_trigger, self.exception)
