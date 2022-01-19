
class BaseTaskFunction:

    @classmethod
    def function(cls, *args, **kwargs):
        print("[NaN] This is function, will do nothing.")
        pass


    @classmethod
    def initialization(cls, *args, **kwargs) -> None:
        print("[NaN] This is initialization, will do nothing.")
        pass


    @classmethod
    def done_handler(cls, result):
        print("[NaN] This is done-handler, will do nothing.")
        return result


    @classmethod
    def error_handler(cls, e: Exception):
        print("[NaN] This is error-handler, will do nothing.")
        return e



class SharedTask:

    __Function = None
    __Func_Args = None
    __Func_Kwargs = None
    __Initialization = None
    __Done_Handler = None
    __Error_Handler = None

    def __init__(self):
        self.__Initialization = BaseTaskFunction.initialization
        self.__Done_Handler = BaseTaskFunction.done_handler
        self.__Error_Handler = BaseTaskFunction.error_handler


    @property
    def function(self):
        return self.__Function


    def set_func(self, func):
        self.__Function = func


    @property
    def func_args(self):
        return self.__Func_Args


    def set_func_args(self, args):
        self.__Func_Args = args


    @property
    def initialization(self):
        return self.__Initialization


    @property
    def func_kwargs(self):
        return self.__Func_Kwargs


    def set_func_kwargs(self, kwargs):
        self.__Func_Kwargs = kwargs


    @property
    def done_handler(self):
        return self.__Done_Handler


    @property
    def error_handler(self):
        return self.__Error_Handler

