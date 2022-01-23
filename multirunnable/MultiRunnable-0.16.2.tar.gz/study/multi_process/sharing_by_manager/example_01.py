from multiprocessing.managers import BaseManager
import multiprocessing


class MyManager(BaseManager):
    pass


def Manager():
    m = MyManager()
    m.start()
    return m


class Counter:

    def __init__(self):
        self._value = 0

    def update(self, value):
        self._value += value

    def get_value(self):
        return self._value


MyManager.register('Counter', Counter)


def update(counter_proxy, thread_id):
    counter_proxy.update(1)
    print(counter_proxy.get_value(), 't%s' % thread_id, multiprocessing.current_process().name)
    return counter_proxy


manager = Manager()
counter = manager.Counter()


def test_update(thread_id):
    counter.update(1)
    print(counter.get_value(), 't%s' % thread_id, multiprocessing.current_process().name)
    return counter


def main():
    # manager = Manager()
    # counter = manager.Counter()
    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    for i in range(10):
        pool.apply(func=test_update, args=(i,))
    pool.close()
    pool.join()


if __name__ == '__main__':

    main()


