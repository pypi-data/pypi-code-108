from typing import List


class Coroutine:
    def __init__(self, handler, batch_size=10, sleep=0):
        self.__handler = handler
        self.batch_size = batch_size
        self.sleep = sleep

    def run_all(self, func, func_args: List[dict], batch_size=None, sleep=None, raise_error=True, **kwargs):
        for i in self.item_range(func_args, batch_size):
            workers = [self.__handler.spawn_later(sleep or self.sleep, func, **j) for j in func_args[i[0]:i[1]]]
            self.__handler.joinall(workers, raise_error=raise_error, **kwargs)
            yield [res.value for res in workers]

    def item_range(self, items: list, batch_size=None):
        batch_siez = batch_size or self.batch_size
        for i in range(0, len(items), batch_siez):
            cursor = i
            yield cursor, cursor + batch_siez
