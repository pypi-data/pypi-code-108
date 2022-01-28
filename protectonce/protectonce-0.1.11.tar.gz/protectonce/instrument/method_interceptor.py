from os import stat

from .base_interceptor import BaseInterceptor


class MethodInterceptor(BaseInterceptor):
    """ MethodInterceptor is a helper class which intercepts a give method 
        to add a pre and post hook
    """

    def __init__(self, mod, cls, methods, handlers) -> None:
        super().__init__(mod, cls, methods, handlers)

    def intercept(self) -> None:
        methods = self._methods.keys()
        for method in methods:
            self._wrap_method(
                method, MethodInterceptor.get_wrapper(method, self))

    @staticmethod
    def get_wrapper(method_name, interceptor):
        def wrapper(wrapped, instance, args, kwargs):
            interceptor.pre_callbacks(method_name, *args, **kwargs)

            result = wrapped(*args, **kwargs)

            interceptor.post_callbacks(method_name, result, *args, **kwargs)
            return result

        return wrapper
