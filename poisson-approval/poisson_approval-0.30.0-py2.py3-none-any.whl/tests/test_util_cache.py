import pytest
from poisson_approval.utils.UtilCache import cached_property, DeleteCacheMixin, property_deleting_cache


def test():
    """
    In the following example, in the last instruction, foo must not be computed again:

        >>> class MyClass:
        ...
        ...     @cached_property
        ...     def foo(self):
        ...         print('Computing foo...')
        ...         return 'result_foo'
        ...
        ...     @cached_property
        ...     def foobar(self):
        ...         print('Computing foobar...')
        ...         return self.foo + 'bar'
        >>> my_object = MyClass()
        >>> print(my_object.foobar)
        Computing foobar...
        Computing foo...
        result_foobar
        >>> print(my_object.foo)
        result_foo
    """
    pass


def test_property_deleting_cache():

    class MyClass(DeleteCacheMixin):
        def __init__(self, some_parameter):
            self.some_parameter = some_parameter
        some_parameter = property_deleting_cache('_some_parameter')

        @cached_property
        def my_cached_property(self):
            print('Computing my_cached_property...')
            return 'Hello %s!' % self.some_parameter

    my_object = MyClass(some_parameter='World')
    assert my_object.my_cached_property == 'Hello World!'
    del my_object.some_parameter
    with pytest.raises(AttributeError):
        print(my_object.my_cached_property)
