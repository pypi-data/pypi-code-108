from typing import Callable



class Decorator:

    """
    The class which is the decorator.
    """

    def __init__(self, function):
        self.function = function
        self.mode = "test mode"


    def attr_1(self):
        return "Attribute 1"


class SavingObj:

    __Value1 = ""
    __Value2 = ""

    def value1(self):
        return self.__Value1


    def set_value1(self, val):
        self.__Value1 = val


    def value2(self):
        return self.__Value2


    def set_value2(self, val):
        self.__Value2 = val


class SuperDecoratorCls:

    def retry_mechanism(function: Callable):
        """
        The function which is decorator.
        :return:
        """

        def retry(*args, **kwargs):
            try:
                print("Run the function ...")
                function(*args, **kwargs)
            except Exception as e:
                print("Catch the exception!")
                print(e)
            else:
                print("Run successfully!")
            finally:
                print("Test done.")
        return retry


    def task_retry_mechanism(function: Callable):
        """
        The function which is decorator.
        :return:
        """

        def task_retry(self, task: SavingObj):
            try:
                print("Run the inner function ...")
                self.test_cls_method()
                print("Run the function ...")
                print("This is task content: ", task)
                print("This is task content value1: ", task.value1())
                print("This is task content value2: ", task.value2())
                function(task)
            except Exception as e:
                print("Catch the exception!")
                print(e)
            else:
                print("Run successfully!")
            finally:
                print("Test done.")
        return task_retry


    def test_cls_method(self):
        print("This is 'SuperDecoratorCls' class method.")



class DecoratorCls:

    def target_fun(self):
        """
        General function without any operation.
        :return:
        """

        print("This is a testing function.")


    @SuperDecoratorCls.retry_mechanism
    def target_fun_with_retry(self, *args, **kwargs):
        """
        Decorate with function.
        :param args:
        :param kwargs:
        :return:
        """

        if args or kwargs:
            print("get args: ", args)
            print(" or ")
            print("get kwargs: ", kwargs)
        print("Is it raise exception?")
        raise Exception("Just for test")


    @SuperDecoratorCls.task_retry_mechanism
    def target_fun_with_task_retry(self, task: SavingObj):
        """
        Decorate with function.
        :param task:
        :return:
        """

        if task.value1() or task.value2():
            print("get task.value1: ", task.value1())
            print(" or ")
            print("get task.value2: ", task.value2())
        print("Is it raise exception?")
        raise Exception("Just for test")


    @Decorator
    def target_fun_with_cls(*args, **kwargs):
        """
        Decorate with class.
        :param args:
        :param kwargs:
        :return:
        """

        if args or kwargs:
            print("get args: ", args)
            print(" or ")
            print("get kwargs: ", kwargs)
        print("Decorate with a class object.")


    def call_decorator_fun(self):
        """
        Call the function which be decorated with function.
        :return:
        """

        print("Call the function which with decorator")
        self.target_fun_with_retry()


    def call_decorator_fun_cls(self):
        """
        Call the function which be decorated with class.
        :return:
        """

        print("Call the function which with class type decorator")
        __fun_with_cls = self.target_fun_with_cls
        __fun_with_cls.function()
        print("mode: ", __fun_with_cls.mode)
        print("attribute: ", __fun_with_cls.attr_1())



if __name__ == '__main__':

    __dc = DecoratorCls()

    __dc.target_fun()

    __dc.target_fun_with_retry("arg1", "arg2")
    __dc.target_fun_with_retry(par1="par1", par2="par2")
    __so = SavingObj()
    __so.set_value1(val="87_value")
    __so.set_value2(val="7878_value")
    __dc.target_fun_with_task_retry(task=__so)

    fun_with_cls = __dc.target_fun_with_cls
    fun_with_cls.function()
    print("mode: ", fun_with_cls.mode)
    print("attribute: ", fun_with_cls.attr_1())

    __dc.call_decorator_fun()
    __dc.call_decorator_fun_cls()
