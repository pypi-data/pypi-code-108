import inspect


class IncompatiblePythonImplementation(Exception):
    pass


class MissingStackContext(Exception):
    pass


_CONTEXT_LOOKUP = {}


def put_stackcontext(key, value):
    def wrapper(fn):
        def impl(*args, **kwargs):
            frame = inspect.currentframe()

            if frame is None:
                raise IncompatiblePythonImplementation()

            try:
                context = _CONTEXT_LOOKUP.get(frame, {})

                context[key] = (value()
                                if inspect.isfunction(value)
                                else value)

                _CONTEXT_LOOKUP[frame] = context

                return fn(*args, **kwargs)
            finally:
                del context[key]

                if len(context) == 0:
                    del _CONTEXT_LOOKUP[frame]

                del frame
        return impl
    return wrapper


def get_stackcontext(key, fallback=None):
    ptr = inspect.currentframe()

    while ptr is not None:
        if ptr in _CONTEXT_LOOKUP:
            context = _CONTEXT_LOOKUP[ptr]
            if key in context:
                return context[key]

        ptr = ptr.f_back

    if fallback is not None:
        return fallback

    raise MissingStackContext()
