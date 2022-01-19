import multiprocessing as mp
from multiprocessing.managers import BaseManager, BaseProxy, MakeProxyType
import os
import time


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


def worker1(f):
    print(f'worker pid={os.getpid()} x={f.get_x()}')
    f.set_x(5)


def worker2(f):
    time.sleep(1)
    print(f'worker pid={os.getpid()} x={f.get_x()}')



if __name__ == '__main__':

    # client, connect to manager server and get data from shared class
    print(f'client running on proc {os.getpid()}')

    MyBaseManager.register("Foo", None, FooProxy)
    m = MyBaseManager(address=(IP, PORT), authkey=KEY)
    m.connect()

    print(f'(proxy) {str(m)}')
    print(f'(referant) {repr(m)}')

    # get copy of managed class proxy and get value, should be 10
    f = m.Foo()
    f.set_x(7)
    print(f'client x={f.get_x()}')
    mp.Process(target=worker1, args=(f,)).start()
    mp.Process(target=worker2, args=(f,)).start()
