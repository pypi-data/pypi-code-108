from __future__ import unicode_literals
import tornado
import functools


def get_exc_info(future):
    '''
    This method creates the exc_info tuple for tornado>=5 in which future.exc_info() method has been removed

    '''
    exc_info = getattr(future, 'exc_info', None)
    if callable(exc_info):
        return exc_info()
    else:
        exception = future.exception()
        if exception:
            return (exception.__class__,
                    exception,
                    getattr(exception, '__traceback__', None))
        else:
            return None


def add_callback(future, end_exit_call_func, exit_call):
    '''
    Used for addition of callback in future for tornado
    tornado < 5, uses tornado.concurrent.futures package which has future._callbacks as an empty list
    tornado >=5, uses asyncio.Futures in presence of asyncio, in which we cannot insert callback at first position as
                 the futures._callbacks is non-writable object. It returns None when
    Tornado >=6, context_vars is used in place of stack_context
    '''
    def wrap_function(end_exit_call_func, exit_call):
        if int(tornado.version.split('.')[0]) >= 6:
            ret = functools.partial(end_exit_call_func, exit_call)
        else:
            return functools.partial(tornado.stack_context.wrap(end_exit_call_func), exit_call)
        import sys
        if (3, 7) > sys.version_info >= (3, 5, 3):
            from appdynamics.agent.core.context import _get_context
            # Run the task in the context so that end_exit_call_func can access current bt
            return functools.partial(_get_context().run, ret)
        return ret

    try:
        from asyncio import Future
        if isinstance(future, Future):
            future.add_done_callback(wrap_function(end_exit_call_func, exit_call))
        else:
            future._callbacks.insert(0, wrap_function(end_exit_call_func, exit_call))
    except ImportError:
        future._callbacks.insert(0, wrap_function(end_exit_call_func, exit_call))
