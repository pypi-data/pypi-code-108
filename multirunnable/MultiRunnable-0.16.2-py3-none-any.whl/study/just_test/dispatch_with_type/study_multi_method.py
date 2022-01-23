from typing import Type, TypeVar, Union
from multimethod import multimethod, overload, isa, multimeta



class ACls:
    pass


class BCls:
    pass


class CCls:
    pass


class DCls:
    pass


class SubACls(ACls):
    pass


class SubBCls(BCls):
    pass


TypeA = TypeVar("TypeA", bound=ACls)
TypeB = TypeVar("TypeB", bound=BCls)


class TestMultiMethod:

    """
    Note:
        This way not work currently ...
    """

    @multimethod
    def test_overload_with_cls(self, param: TypeA):
        print(f"param: {param}")
        print(f"Index is ACls.")


    @test_overload_with_cls.register(ACls)
    def _(self, param: TypeA):
        print(f"param: {param}")
        print(f"Index is ACls.")


    @test_overload_with_cls.register(BCls)
    @test_overload_with_cls.register(CCls)
    def _(self, param: Union[TypeB, CCls]):
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



class TestOverload:

    """
    Note:
        This way mostly like Java style.

        Please make attention for the parameter type-hint: isa. It
        will raise 'TypeError: {Your class}() takes no arguments' error
        if you don't add it.
    """

    @overload
    def test_overload_with_cls(self, param: isa(ACls)):
        print(f"param: {param}")
        print(f"Index is ACls.")


    @overload
    def test_overload_with_cls(self, param: isa(BCls)):
        print(f"param: {param}")
        print(f"Index is BCls.")


    @overload
    def test_overload_with_cls(self, param: isa(CCls)):
        print(f"param: {param}")
        print(f"Index is CCls.")



class TestOverloadMeta(metaclass=multimeta):

    """
    Note:
        This way is very clear and easy (just set meta-class).
    """

    def test_overload_with_cls(self, param: ACls):
        print(f"param: {param}")
        print(f"Index is ACls.")


    def test_overload_with_cls(self, param: BCls):
        print(f"param: {param}")
        print(f"Index is BCls.")


    def test_overload_with_cls(self, param: CCls):
        print(f"param: {param}")
        print(f"Index is CCls.")



if __name__ == '__main__':

    # The parameter values for testing overload feature in Python.
    __a = ACls()
    __sub_a = SubACls()
    __b = BCls()
    __sub_b = SubBCls()
    __c = CCls()
    __d = DCls()

    print(f"++++++++++ Dispatch with Class by multimethod ++++++++++")
    __testc = TestMultiMethod()

    __testc.test_overload_with_cls(__a)
    __testc.test_overload_with_cls(__sub_a)
    __testc.test_overload_with_cls(__b)
    __testc.test_overload_with_cls(__sub_b)
    __testc.test_overload_with_cls(__c)
    # __testc.test_overload_with_cls(__d)    # (No) Raise multimethod.DispatchError

    print(f"++++++++++ Dispatch with Class by overload ++++++++++")
    __to = TestOverload()

    __to.test_overload_with_cls(__a)
    __to.test_overload_with_cls(__sub_a)
    __to.test_overload_with_cls(__b)
    __to.test_overload_with_cls(__sub_b)
    __to.test_overload_with_cls(__c)
    # __to.test_overload_with_cls(__d)    # Raise multimethod.DispatchError

    print(f"++++++++++ Dispatch with Class by meta-class ++++++++++")
    __tom = TestOverloadMeta()

    __tom.test_overload_with_cls(__a)
    __tom.test_overload_with_cls(__sub_a)
    __tom.test_overload_with_cls(__b)
    __tom.test_overload_with_cls(__sub_b)
    __tom.test_overload_with_cls(__c)
    # __tom.test_overload_with_cls(__d)    # Raise multimethod.DispatchError
