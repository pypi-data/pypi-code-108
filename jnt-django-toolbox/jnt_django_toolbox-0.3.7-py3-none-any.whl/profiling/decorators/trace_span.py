import itertools
from functools import wraps

from django.conf import settings
from opentracing import global_tracer


def trace_span(show_args: bool = False):
    """Wrap function for jaeger tracing."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):  # noqa: WPS430
            from jnt_django_toolbox.profiling.profilers import JaegerProfiler

            is_tracing = any(
                isinstance(profiler, JaegerProfiler)
                for profiler in settings.REQUEST_PROFILERS
            )
            if not is_tracing:
                return func(*args, **kwargs)

            caller = None
            if args:
                caller = args[0].__class__

            operation_name = "{0}.{1}{2}".format(
                func.__module__,
                "{0}.".format(caller.__name__) if caller else "",
                func.__name__,
            )
            if show_args:
                operation_name = "{0} [{1}]".format(
                    operation_name,
                    ", ".join(
                        itertools.chain(
                            [str(arg) for arg in args],
                            [
                                "{0}={1}".format(kwarg_key, kwarg_value)
                                for kwarg_key, kwarg_value in kwargs.items()
                            ],
                        ),
                    ),
                )

            with global_tracer().start_active_span(
                operation_name,
                child_of=global_tracer().active_span,
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator
