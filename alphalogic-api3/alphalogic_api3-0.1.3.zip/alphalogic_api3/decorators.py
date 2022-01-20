# -*- coding: utf-8 -*-
import inspect
import time
import traceback
from alphalogic_api3.logger import log
from alphalogic_api3.utils import decode_string, get_command_argument_type


def command_preparation(wrapped, func, **kwargs_c):
    """
    Return value and command arguments setup
    """
    wrapped.result_type = kwargs_c['result_type']
    (args, varargs, keywords, defaults) = inspect.getargspec(func)
    wrapped.__dict__['arguments'] = []
    wrapped.__dict__['arguments_type'] = {}
    wrapped.__dict__['function_name'] = func.__name__
    wrapped.__dict__['choices'] = {}
    for name_arg in list(filter(lambda x: x in kwargs_c, args)):
        wrapped.choices[name_arg] = kwargs_c[name_arg]
    bias = 1 if 'self' in args else 0  # if first arg is self, see from second
    for index, name in enumerate(args[bias:]):
        wrapped.arguments.append((name, defaults[index]))
        wrapped.arguments_type[name] = get_command_argument_type(defaults[index])


def command(*argv_c, **kwargs_c):
    """
    Use this decorator to create :class:`~alphalogic_api3.objects.command.Command` object.

    Example 1::

        # The command returns True every time
        @command(result_type=bool)
        def cmd_exception(self):
            # do smth
            return True

    Example 2::

        # The command has three arguments and returns 'where' argument value
        @command(result_type=bool)
        def cmd_alarm(self, where='here', when=datetime.datetime.now(), why=2):
            return where

    Example 3::

        # The command hasn't arguments and return dict type
        @command(result_type=dict)
        def cmd_alarm(self):
            return {'a': 1, 'b': 'second', 'c': [1,2,3], 'd' : [1, {'2': 3}, 3]}


    :arg result_type: Command return type
    """
    def decorator(func):
        def wrapped(device, *argv, **kwargs):
            try:
                result = func(device, *argv, **kwargs)
                device.__dict__[wrapped.function_name].set_result(result)
                return result
            except Exception as err:
                t = traceback.format_exc()
                log.error(f'Command: function exception: {t}')
                try:
                    device.__dict__[wrapped.function_name].set_exception(t)
                except Exception as err:
                    t = traceback.format_exc()
                    log.error(f'Command: Exception in exception: {t}')

        command_preparation(wrapped, func, **kwargs_c)
        return wrapped
    return decorator


def run(*argv_r, **kwargs_r):
    """
    | This function is used to be called periodically by the gRPC process.
    | It can be defined inside the Object class body to implement some repeatable tasks like interrogation of the controller, modem, database, etc.
    | It is required to specify the necessary trigger period in seconds in the argument of the function.

    Example: ::

        # Called every 1 second.
        # You can change period by changing 'period_one' parameter.

        @run(period_one=1)
        def run_one(self):
            self.counter.val += 1
    """
    def decorator(func):
        def wrapped(device, call_again=False):
            with device.mutex:
                if not device.flag_removing:
                    try:
                        status_perform = True
                        time_start = time.time()
                        try:
                            func(device)
                        except Exception as err:
                            t = traceback.format_exc()
                            log.error(f'Run function exception: {t}')

                        time_finish = time.time()
                        time_spend = time_finish-time_start
                        log.info('run function {0} of device {2} was executed for {1} seconds'.
                                 format(func.__name__, time_spend, device.id))

                        period = getattr(device, list(kwargs_r.keys())[0]).val
                        func.__dict__['mem_period'] = period

                    except Exception as err:
                        t = traceback.format_exc()
                        log.error(f'system error in run decorator: {t}')
                        status_perform = False
                    finally:
                        if not status_perform:
                            mem_period = func.__dict__['mem_period'] \
                                if 'mem_period' in func.__dict__ \
                                else list(kwargs_r.values())[0]
                        else:
                            mem_period = period

                        if call_again:
                            if time_spend < mem_period:
                                device.manager.tasks_pool.add_task(time_finish + mem_period - time_spend,
                                                                   getattr(device, func.__name__))
                            else:
                                device.manager.tasks_pool.add_task(time_finish, getattr(device, func.__name__))

        wrapped.runnable = True
        wrapped.period_name = list(kwargs_r.keys())[0]
        wrapped.period_default_value = list(kwargs_r.values())[0]
        return wrapped
    return decorator