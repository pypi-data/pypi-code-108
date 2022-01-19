from functools import update_wrapper, partial, wraps
from typing import Callable



class TestDecorator:

    def __init__(self, function: Callable, param=""):
        update_wrapper(self, function)
        self.function = function
        self._param = param

    def __get__(self, instance, owner):
        print("In Get ...")
        print(f"instance: {instance}")
        print(f"owner: {owner}")
        print("In Get ...")
        return partial(self.__call__, instance)

    def __call__(self, instance, *args, **kwargs):
        print("Running function ...")
        print(f"instance: {instance}")
        print(f"function: {self.function}")
        print(f"args: {args}")
        print(f"kwargs: {kwargs}")
        return self.function(instance, *args, **kwargs)


def test_decorator(function=None):
    if function:
        return TestDecorator(function=function)
    else:
        @wraps(function)
        def _wrapper(function):
            return TestDecorator(function=function)
        return _wrapper


class TestCls:

    @test_decorator
    def main_code(self):
        # print(f"index: {index}")
        print("This is function for testing.")
        return "Fuck"



if __name__ == '__main__':

    __tc = TestCls()
    # __tc.main_code(index="params")
    result = __tc.main_code()
    print(f"result: {result}")
