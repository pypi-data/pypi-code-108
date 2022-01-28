from Timeout import *
from time import sleep
from multiprocessing import freeze_support


class A:
    def __init__(self):
        self.a = "a"


def test1(arg1, arg2, kwarg1=None, kwarg2=None):
    print("test1")
    assert arg1
    assert arg2
    assert kwarg1
    assert kwarg2
    sleep(1)
    return A(), A(), sleep


def test6(arg1, arg2, kwarg1=None, kwarg2=None):
    assert arg1
    assert arg2
    assert kwarg1
    assert kwarg2

    while 1:
        print("test6")
        sleep(1)

    return A(), A(), sleep


def main2():
    print(
        function1(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    )

    try:
        function6(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    except TimeoutError:
        pass
    else:
        assert False


function1 = process_timeout(5)(test1)  # function wrapped
function6 = process_timeout(5)(test6)  # function wrapped

if __name__ == "__main__":
    freeze_support()
    main2()


class Test2:

    test_ = True

    def __init__(self):
        self.test = True

    @process_timeout(3)
    def test3(self, arg1, arg2, kwarg1=None, kwarg2=None):
        print("test3")
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2
        assert self.test
        assert self.test_
        sleep(1)
        return A(), A(), sleep

    @process_timeout(3)
    def test8(self, arg1, arg2, kwarg1=None, kwarg2=None):
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2
        assert self.test
        assert self.test_

        while 1:
            print("test8")
            sleep(1)

        return A(), A(), sleep

    @staticmethod
    @process_timeout(3)
    def test4(arg1, arg2, kwarg1=None, kwarg2=None):
        print("test4")
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2
        sleep(1)
        return A(), A(), sleep

    @staticmethod
    @process_timeout(3)
    def test9(arg1, arg2, kwarg1=None, kwarg2=None):
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2

        while 1:
            print("test9")
            sleep(1)

        return A(), A(), sleep

    @process_timeout(3)
    @classmethod
    def test5(cls, arg1, arg2, kwarg1=None, kwarg2=None):
        print("test5")
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2
        assert cls.test_
        sleep(1)
        return A(), A(), sleep

    @process_timeout(3)
    @classmethod
    def testA(cls, arg1, arg2, kwarg1=None, kwarg2=None):
        assert arg1
        assert arg2
        assert kwarg1
        assert kwarg2
        assert cls.test_

        while 1:
            print("testA")
            sleep(1)

        return A(), A(), sleep


@process_timeout(3)
def test2(arg1, arg2, kwarg1=None, kwarg2=None):
    print("test2")
    assert arg1
    assert arg2
    assert kwarg1
    assert kwarg2
    sleep(1)
    return A(), A(), sleep


@process_timeout(3)
def test7(arg1, arg2, kwarg1=None, kwarg2=None):
    assert arg1
    assert arg2
    assert kwarg1
    assert kwarg2

    while 1:
        print("test7")
        sleep(1)

    return A(), A(), sleep


def main3():
    print(
        test2(1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc")
    )

    try:
        test7(1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc")
    except TimeoutError:
        pass
    else:
        assert False

    t = Test2()

    print(
        t.test3(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    )
    print(
        t.test4(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    )
    print(
        t.test5(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    )

    try:
        t.test8(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    except TimeoutError:
        pass
    else:
        assert False

    try:
        t.test9(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    except TimeoutError:
        pass
    else:
        assert False

    try:
        t.testA(
            1, True, [1.6, None, {"test"}, {0: 0}, ("test",)], kwarg2="abc"
        )
    except TimeoutError:
        pass
    else:
        assert False


if __name__ == "__main__":
    main3()
