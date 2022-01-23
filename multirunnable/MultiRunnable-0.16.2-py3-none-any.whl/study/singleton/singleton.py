
def singleton(_class):

    class _SingletonClass(_class):

        _Instance = None

        def __new__(_class, *args, **kwargs):
            if _SingletonClass._Instance is None:
                _SingletonClass._Instance = super(_SingletonClass, _class).__new__(_class, *args, **kwargs)
                _SingletonClass._Instance._sealed = False
            return _SingletonClass._Instance


        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(_SingletonClass, self).__init__(*args, **kwargs)
            self._sealed = True

    _SingletonClass.__name__ = _class.__name__
    return _SingletonClass



@singleton
class TestCls:

    def test(self):
        print("This is test function.")



if __name__ == '__main__':

    tc_1 = TestCls()
    tc_2 = TestCls()

    tc_1_id = id(tc_1)
    tc_2_id = id(tc_2)

    print("id(tc_1): ", tc_1_id)
    print("id(tc_2): ", tc_2_id)

