from multiprocessing.managers import BaseManager, BaseProxy, MakeProxyType
import os

IP = 'localhost'
PORT = 50000
KEY = b'abracadabra'

#  proxy class
FooProxyBase = MakeProxyType('FooProxyBase', ('get_x', 'set_x'))


class FooProxy(FooProxyBase):
    """shared class proxy"""

    def get_x(self):
        return self._callmethod('get_x')

    def set_x(self, value):
        return self._callmethod('set_x', (value,))


# custom shared class manager
class MyBaseManager(BaseManager):
    pass


# client, connect to manager server and get data from shared class
print(f'client running on proc {os.getpid()}')

MyBaseManager.register("Foo", None, FooProxy)
MyBaseManager.register("get_foo")
m = MyBaseManager(address=(IP, PORT), authkey=KEY)
m.connect()

print(f'(proxy) {str(m)}')
print(f'(referant) {repr(m)}')

# get global instance and get value, should be 10
f = m.get_foo()
print(f'x={f.get_x()} => should be 10')

