from typing import Tuple, List


class Math:
    def __init__(self):
        ...

    def n_fib(self, n: int) -> int:
        '''https://stackoverflow.com/questions/4935957/fibonacci-numbers-with-an-one-liner-in-python-3'''
        return pow(2 << n, n + 1, (4 << 2 * n) - (2 << n) - 1) % (2 << n)

    def fibs(self, n: int) -> List[int]:
        return list(map(self.n_fib, range(1, n + 1)))


math = Math()
