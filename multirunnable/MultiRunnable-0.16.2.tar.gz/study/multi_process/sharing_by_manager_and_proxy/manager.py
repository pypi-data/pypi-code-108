from multiprocessing.managers import BaseManager, BaseProxy, MakeProxyType
import os

IP = 'localhost'
PORT = 50000
KEY = b'abracadabra'


# shared class
class Foo:
    """my custom shared class"""
    def __init__(self):
        self.x = None

    def get_x(self):
        return self.x

    def set_x(self, value):
        self.x = value


#  proxy class
FooProxyBase = MakeProxyType('FooProxyBase', ('get_x', 'set_x'))


class FooProxy(FooProxyBase):
    """shared class proxy"""

    def get_x(self):
        return self._callmethod('get_x')

    def set_x(self, value):
        return self._callmethod('set_x', (value,))


##  Global Foo and function to get the instance.
global_foo = Foo()


def get_foo():
    return global_foo


# custom shared class manager
class MyBaseManager(BaseManager):
    pass


if __name__ == '__main__':

    # manager, run manager server for shared class and set data
    print(f'manager running on proc {os.getpid()}')

    MyBaseManager.register("Foo", Foo, FooProxy)
    MyBaseManager.register("get_foo", get_foo)
    m = MyBaseManager(address=(IP, PORT), authkey=KEY)
    m.start()

    print(f'manager server running on proc {m._process.pid}')
    print(f'(proxy) {str(m)}')
    print(f'(referant) {repr(m)}')

    # get global instance and set value to 10
    f = m.get_foo()
    print(f'x={f.get_x()} => should be None')
    f.set_x(10) # set x value to 10
    print(f'x={f.get_x()} => should be 10')
