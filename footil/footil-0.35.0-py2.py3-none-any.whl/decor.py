"""Module providing various helper decorators."""
import time
import logging
import inspect
from typing import Optional, Union, Dict

from . import formatting


def _get_stdout_writer(
        stdout_writer=None, stdout_getter=None, args=None, kwargs=None):
    if stdout_writer:
        return stdout_writer
    if stdout_getter:
        args = args or ()
        kwargs = kwargs or {}
        return stdout_getter(*args, **kwargs)
    return print


def _default_interpolation(pattern, args):
    return (pattern % args, )


def _lazy_interpolation(pattern, args):
    return (pattern, args)


def _get_interpolation_func(lazy=False):
    if lazy:
        return _lazy_interpolation
    return _default_interpolation


def _get_stdout_input_args(func, options, args=None, kwargs=None):
    if not args:
        args = ()
    if not kwargs:
        kwargs = {}
    interpolation = _get_interpolation_func(
        options.get('lazy_interpolation', False))
    pattern, pattern_args = formatting.format_func_input(
        func.__name__,
        command=options.get('command', False),
        no_first_arg=options.get('no_first_arg', False),
        prefix=options.get('prefix', ''),
        args=args,
        kwargs=kwargs)
    return interpolation(pattern, pattern_args)


def _get_stdout_output_args(options, output):
    interpolation = _get_interpolation_func(
        options.get('lazy_interpolation', False))
    return interpolation('%s%s', (options.get('prefix', ''), output))


def stdout_input(
        options: Union[
            None,
            Dict,
        ] = None):
    """Log function's call input.

    Args:
        options: options to customize input's stdout formatting:
            stdout_writer: function that writes to stdout. If
                stdout_writer stdout_getter are not specified, will
                default to `print` function.
            stdout_getter: function to get stdout function that would be
                used in writing stdout. Will use original function's
                *args, **kwargs in call.
            lazy_interpolation: whether to let stdout_writer to handle
                string interpolation.
            no_first_arg: whether to not include first argument in
                formatted string.
            prefix: whether to set custom prefix before formatted
                string.
            command: whether call it as shell like. If set to True, will
                format input without wrapping args/kwargs with
                parenthesis.
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            stdout_writer = _get_stdout_writer(
                stdout_writer=options.get('stdout_writer'),
                stdout_getter=options.get('stdout_getter'),
                args=args,
                kwargs=kwargs
            )
            stdout_args = _get_stdout_input_args(
                func, options, args=args, kwargs=kwargs)
            stdout_writer(*stdout_args)
            return func(*args, **kwargs)
        return wrapper

    if not options:
        options = {}
    return inner


def stdout_output(
        options: Union[
            None,
            Dict,
        ] = None):
    """Log function's call output.

    Args:
        options: options to customize output's stdout formatting:
            stdout_writer: function that writes to stdout. If
                stdout_writer stdout_getter are not specified, will
                default to `print` function.
            stdout_getter: function to get stdout function that would be
                used in writing stdout. Will use original function's
                *args, **kwargs in call.
            lazy_interpolation: whether to let stdout_writer to handle
                string interpolation.
            prefix: whether to set custom prefix before formatted
                string.
    """
    def inner(func):
        def wrapper(*args, **kwargs):
            stdout_writer = _get_stdout_writer(
                stdout_writer=options.get('stdout_writer'),
                stdout_getter=options.get('stdout_getter'),
                args=args,
                kwargs=kwargs
            )
            output = func(*args, **kwargs)
            stdout_args = _get_stdout_output_args(
                options, output)
            stdout_writer(*stdout_args)
            return output
        return wrapper

    if not options:
        options = {}
    return inner


class _TimeIt(object):
    """Decorator  class to track function execution time.

    This decorator should probably be used as convenience. If you need
    to benchmark your code, you should probably use standard module
    timeit.
    """

    _time_map = {
        'ms': ('millisecond(s)', 1000),
        's': ('second(s)', 1),
        'm': ('minute(s)', 1/60),
        'h': ('hour(s)', 1/3600),
    }

    def __init__(
        self,
        log_level: Optional[str] = None,
        msg_fmt: str = "'{_f_name}' took {_dur:.2f} {_uom_name}",
            uom: str = 's') -> None:
        """Initialize specified arguments for _TimeIt object.

        Args:
            log_level: logging level to use (default: {None})
            msg_fmt: message format. Possible keys for message format:
                - main:
                  - '_f_name': function name.
                  - '_dur': time it took to execute function (in format
                    specified in time_fmt).
                  - '_uom_name': unit of measure name (second(s),
                    minute(s) etc.).
                - positional arguments: arg0, arg1, arg2 etc. Will name
                    positional arguments (if any) of function that uses
                    this decorator. If function has __self__ attribute,
                    it will be used for arg0.
                - keyword arguments: keyword arguments (if any) of
                    function that uses this decorator.
                (default: {"'{f_name}' took {dur:.2f} {uom_name}"})
            uom: time unit of measure to output. Possible values:
                'ms' (milliseconds), 's' (seconds), 'm' (minutes), 'h'
                (hours) (default: {'s'})
        """
        self.log_level = log_level
        self.msg_fmt = msg_fmt
        self.uom = uom

    def _get_message_vals(self, func, duration, args=None, kwargs=None):

        def insert_args(args, func, vals):
            pos = 0
            if hasattr(func, '__self__'):
                vals['arg0'] = func.__self__
                # Move position to right, because arg0 is now already
                # assigned.
                pos = 1
            for i, arg in enumerate(args, pos):
                vals['arg%s' % i] = arg

        if not args:
            args = ()
        if not kwargs:
            kwargs = {}
        uom_name, uom_ratio = self._time_map[self.uom]
        # Define main vals.
        vals = {
            '_f_name': func.__name__,
            '_dur': duration * uom_ratio,
            '_uom_name': uom_name
        }
        insert_args(args, func, vals)
        # Insert kwargs. Will overwrite old keys if some already exist.
        vals.update(kwargs)
        return vals

    def _get_message(
        self,
        func,
        duration: float,
        args: Optional[tuple] = None,
            kwargs: Optional[dict] = None):
        vals = self._get_message_vals(func, duration, args=args, kwargs=kwargs)
        return self.msg_fmt.format(**vals)

    def output(self, func, duration, args=None, kwargs=None):
        msg = self._get_message(func, duration, args=args, kwargs=kwargs)
        if self.log_level:
            log_level = self.log_level.lower()
            getattr(logging, log_level)(msg)
        else:
            print(msg)

    def __call__(self, func):
        """Wrap function and track time it took to execute it."""
        def wrapped(*args, **kwargs):
            ts = time.time()
            res = func(*args, **kwargs)
            te = time.time()
            self.output(func, te-ts, args=args, kwargs=kwargs)
            return res
        return wrapped


class _CatchExceptions(object):
    """Decorator class to catch exceptions on function run."""

    def __init__(self, exceptions_lst, err_msg_pos=0):
        """Init exceptions config."""
        self.exceptions_lst = exceptions_lst
        self.err_msg_pos = err_msg_pos

    def _get_exceptions(self):
        # tuple is required when using exceptions in catching.
        return tuple(
            [exc_item['exception'] for exc_item in self.exceptions_lst])

    @staticmethod
    def _is_bound_method(method):
        return hasattr(method, '__self__')

    @classmethod
    def _map_args_kwargs(cls, func, *fn_args, **fn_kwargs):
        def combine_args_kwargs(args, kwargs):
            return {'args': tuple(args), 'kwargs': kwargs}

        # Make copies from args and kwargs to not modify original
        # arguments passed. Shallow copy is enough here, because values
        # itself are not modified, only add and remove operations are
        # made.
        args = list(fn_args)  # converted back to tuple in the end.
        kwargs = dict(fn_kwargs)
        spec = inspect.getfullargspec(func)
        # If method is bound, it means first argument is an instance of
        # some class. In that case we insert it into args as first
        # argument.
        if cls._is_bound_method(func):
            args.insert(0, func.__self__)
        # If we have *args, it means kwargs can't be specified as
        # positional arguments or if we do not have defaults, it means
        # only positional arguments can be used as positional. In both
        # cases, no further mapping is needed.
        if spec.varargs or not spec.defaults:
            return combine_args_kwargs(args, kwargs)
        # Get number of kw and real positional arguments.
        kwargs_num = len(spec.defaults)
        args_num = len(spec.args)
        real_args_num = args_num - kwargs_num
        # Check if real positional arguments match all positional
        # arguments. If it does, it means all kwargs were used as kwargs
        # and not as positional arguments.
        fake_args_num = len(args) - real_args_num
        if not fake_args_num:
            return combine_args_kwargs(args, kwargs)
        # Find kwargs that are used as positional arguments.
        args = list(args)
        # pop fake positional arguments and put it back into kwargs.
        # Need to start from the end of index range, because poping
        # items in increasing order, would mess up index.
        for index in range(real_args_num+fake_args_num-1, real_args_num-1, -1):
            kwargs[spec.args[index]] = args.pop(index)
        return combine_args_kwargs(args, kwargs)

    def __call__(self, fn, *args, **kwargs):
        """Catch defined exceptions and output specified message."""
        def new_func(*args, **kwargs):
            # TODO: allow specifying __self__ attributes to be used
            # in message.
            def parse_params(e, params=False):
                args_kwargs = self._map_args_kwargs(fn, *args, **kwargs)
                if not params:
                    params = []
                values = []
                # key for args is index, for kwargs, it is dictionary
                # key.
                for key, _type in params:
                    # Access value from args or kwargs and add it to
                    # list.
                    values.append(args_kwargs[_type][key])
                # Combine with error message if error_msg_pos is not
                # False.
                if self.err_msg_pos is not False:
                    values.insert(self.err_msg_pos, e)
                return tuple(values)

            exceptions = self._get_exceptions()
            try:
                return fn(*args, **kwargs)
            except exceptions as e:
                for exc_dct in self.exceptions_lst:
                    exception = exc_dct['exception']
                    # Check if specific condition matches what is defined
                    # in exception catching config.
                    if isinstance(e, exception):
                        exc_condition = exc_dct.get('exc_condition')
                        # Check if exception has condition (such as specific
                        # error code) and run it.
                        if not exc_condition or exc_condition(e):
                            exc_to_raise = (
                                exc_dct.get('raise_exception') or exception)
                            values = parse_params(e, exc_dct.get('params'))
                            raise exc_to_raise(exc_dct['msg'] % values)
                raise
        return new_func


time_it = _TimeIt
catch_exceptions = _CatchExceptions
