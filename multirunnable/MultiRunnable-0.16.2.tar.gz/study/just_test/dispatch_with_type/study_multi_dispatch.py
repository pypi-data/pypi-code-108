from base import BaseACls, BaseBCls
from typing import Type, TypeVar, Union
from types import MethodType, FunctionType
from collections import Callable
from multipledispatch import dispatch



class ACls(BaseACls):
    pass


class BCls(BaseBCls):
    pass


class SubACls(ACls):
    pass


class SubBCls(BCls):
    pass


class CCls:
    pass


TypeA = TypeVar("TypeA", bound=ACls)
TypeB = TypeVar("TypeB", bound=BCls)



# class TestCallable(Callable):
#     pass



class TestDispatch:

    """
    Note
        Using multi-dispatch implement calling different function
        or method with different data-type parameter values.
    """

    @dispatch(BaseACls)
    def test_overload_with_cls(self, param: TypeA):
        print(f"param: {param}")
        print(f"Index is ACls.")


    @dispatch(BaseBCls)
    def test_overload_with_cls(self, param: TypeB):
        print(f"param: {param}")
        print(f"Index is BCls.")


    @dispatch(Callable)
    def test_overload_with_cls(self, param: Callable):
        print(f"param: {param} and it will run it.")
        param()
        print(f"Index is Callable.")


    # @dispatch(Callable)
    # def test_multi_param(self, function, *args):
    #     print(f"param: {args} is a empty tuple type data and it will run it.")
    #     function(*args)
    #     print(f"Index is Callable.")


    @dispatch(MethodType, tuple)
    def test_multi_param(self, function, args):
        print(f"param: {args} is a tuple type data and it will run it.")
        function(*args)
        print(f"Index is Callable.")


    @dispatch(MethodType, dict)
    def test_multi_param(self, function, args):
        print(f"param: {args} is a dict type data and it will run it.")
        function(**args)
        print(f"Index is Callable.")


    @dispatch((BaseACls, CCls))
    def test_overload_other(self, param: Union[TypeA, CCls]):
        print(f"param: {param}")
        print(f"Index type is ACls or CCls.")


    @dispatch(BaseBCls)
    def test_overload_other(self, param: TypeB):
        print(f"param: {param}")
        print(f"Index is BCls.")


    # @dispatch(Type[ACls])
    # def test_overload_with_type(self, param):
    #     print(f"param: {param}")
    #     print(f"Index is ACls.")
    #
    #
    # @dispatch(Type[BCls])
    # def test_overload_with_type(self, param):
    #     print(f"param: {param}")
    #     print(f"Index is BCls.")


class TestCls:

    def test(self, *args, **kwargs):
        print("This is testing function object.")
        print("args: ", args)
        print("kwargs: ", kwargs)


    @staticmethod
    def static_test():
        print("This is staticmethod testing function object.")


    @classmethod
    def class_test(cls):
        print("This is classmethod testing function object.")


def test_func():
    print("This is testing callable object.")


if __name__ == '__main__':

    __a = ACls()
    __sub_a = SubACls()
    __b = BCls()
    __sub_b = SubBCls()
    __c = CCls()

    print(f"++++++++++ Dispatch with Class ++++++++++")
    __testc = TestDispatch()

    # __testc.test_overload_with_cls(__a)
    # __testc.test_overload_with_cls(__sub_a)
    # __testc.test_overload_with_cls(__b)
    # __testc.test_overload_with_cls(__sub_b)
    __tcls = TestCls()
    # __testc.test_overload_with_cls(test_func)
    # __testc.test_overload_with_cls(__tcls.test)
    # __testc.test_overload_with_cls(TestCls.static_test)
    # __testc.test_overload_with_cls(TestCls.class_test)

    # __testc.test_multi_param(__tcls.test, (1, "test_param", ))
    __testc.test_multi_param(__tcls.test, ())
    # __testc.test_multi_param(__tcls.test, )
    __testc.test_multi_param(__tcls.test, {"index": 1, "test_param": "test_val"})

    # __testc.test_overload_other(__a)
    # __testc.test_overload_other(__sub_a)
    # __testc.test_overload_other(__c)
    # __testc.test_overload_other(__b)
    # __testc.test_overload_other(__sub_b)

    # print(f"++++++++++ Dispatch with Type[Class] ++++++++++")
    # __testc.test_overload_with_type(__sub_a)
    # __testc.test_overload_with_type(__b)
