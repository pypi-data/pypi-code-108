def init_check(original_class):
    orig_init = original_class.__init__

    def __init__(self, *args, **kws):
        try:
            orig_init(self, *args, **kws)
            self.__init_result = True
        except BaseException:
            self.__init_result = False

    original_class.__init__ = __init__

    def __bool__(obj):
        return obj.__init_result
    original_class.__bool__ = __bool__

    return original_class
