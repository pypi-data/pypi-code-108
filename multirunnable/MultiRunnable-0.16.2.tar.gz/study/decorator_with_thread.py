from threading import Thread
from typing import Callable



class SuperDecoratorCls:

    def retry_mechanism(function: Callable):
        """
        The function which is decorator.
        :return:
        """

        def retry(args=None, kwargs=None, done_hdlr=None, error_hdlr=None, timeout=0):
            __fun_run_time = 0
            __fun_run_finish = None
            result = None
            while __fun_run_time < timeout:
                try:
                    print("Run the function ...")
                    result = function(*args, **kwargs)
                except Exception as e:
                    error_hdlr(e=e)
                    __fun_run_finish = False
                    result = e
                    print("Catch the exception!")
                    print(e)
                else:
                    result = done_hdlr(result=result)
                    __fun_run_finish = True
                    print("Run successfully!")
                finally:
                    __fun_run_time += 1
                    print("Test done.")
                    return result

        return retry



class SuperDecoratorClsInner:

    Running_Timeout = 1

    # def __init__(self, timeout: int):
    #     # self.__task = task
    #     self.Running_Timeout = timeout

    def __init__(self):
        self.thread_num = 5


    def run_target(self, *args, **kwargs):
        thread_list = [
            Thread(target=self.target_function, args=args, kwargs=kwargs)
            for _ in range(self.thread_num)
        ]
        for t in thread_list:
            t.start()
        for t in thread_list:
            t.join()


    def target_function(self):
        pass


    def retry_mechanism(function: Callable):
        """
        The function which is decorator.
        :return:
        """

        def retry(*args, **kwargs):
            __fun_run_time = 0
            __fun_run_finish = None
            while __fun_run_time < SuperDecoratorClsInner.Running_Timeout:
                try:
                    print("Run the function ...")
                    function(*args, **kwargs)
                except Exception as e:
                    SuperDecoratorClsInner.error_handling(e=e)
                    __fun_run_finish = False
                    print("Catch the exception!")
                    print(e)
                else:
                    SuperDecoratorClsInner.done_handling()
                    __fun_run_finish = True
                    print("Run successfully!")
                finally:
                    __fun_run_time += 1
                    print("Test done.")

        return retry


    @classmethod
    def done_handling(cls):
        print("Handling something when your task done.")


    @classmethod
    def error_handling(cls, e: Exception):
        print("Exception: ", e)
        print("Handling something when your task occur exception.")



class DecoratorCls(SuperDecoratorCls):

    # _DI = SuperDecoratorClsInner(timeout=87)

    def target_fun(self):
        """
        General function without any operation.
        :return:
        """

        print("This is a testing function.")


    @SuperDecoratorClsInner.retry_mechanism
    def target_fun_with_retry(self, *args, **kwargs):
        """
        Decorate with function.
        :return:
        """

        if args or kwargs:
            print("get args: ", args)
            print(" or ")
            print("get kwargs: ", kwargs)
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

    # __dc.target_fun()
    __dc.target_fun_with_retry(task=TestTask(function=__dc.target_fun))

