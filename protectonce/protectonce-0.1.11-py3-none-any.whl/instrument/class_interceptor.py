from os import stat

from wrapt import ObjectProxy

from .method_interceptor import MethodInterceptor


class ClassProxy(ObjectProxy):
    """ This acts as the proxy class to the intercepted class
        Any method from the class can be intercepted by calling add_method
    """

    def __init__(self, wrapper) -> None:
        super(ClassProxy, self).__init__(wrapper)

    @staticmethod
    def add_method(interceptor, method_name):
        def wrapper(self, *args, **kwargs):
            interceptor.pre_callbacks(method_name, None, *args, **kwargs)

            original = getattr(self.__wrapped__, method_name)
            result = original(*args, **kwargs)

            proxy = ClassProxy(result)
            interceptor.post_callbacks(
                method_name, proxy, None, *args, **kwargs)
            return proxy

        setattr(ClassProxy, method_name, wrapper)


class ClassInterceptor(MethodInterceptor):
    """ This intercepts the class creation and returns a proxy object
    """

    def __init__(self, mod, cls, methods, handlers) -> None:
        super(ClassInterceptor, self).__init__(mod, cls, methods, handlers)

    def intercept(self) -> None:
        methods = self._methods.keys()
        for method in methods:
            if isinstance(self._module, ClassProxy):
                ClassProxy.add_method(self, method)
            else:
                super(ClassInterceptor, self)._wrap_method(
                    method, ClassInterceptor.get_wrapper(self, method))

    @staticmethod
    def get_wrapper(interceptor, method_name):
        def wrapper(wrapped, instance, args, kwargs):
            interceptor.pre_callbacks(method_name, instance, *args, **kwargs)

            result = wrapped(*args, **kwargs)
            proxy = ClassProxy(result)

            interceptor.post_callbacks(
                method_name, proxy, instance, *args, **kwargs)
            return proxy

        return wrapper
