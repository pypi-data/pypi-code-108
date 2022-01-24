import os
import time
from multiprocessing import Pool


def work(name):
    print(time.time(), name)
    return f'{name} worked on {time.time()} pid={os.getpid()}'


if __name__ == '__main__':
    with Pool(processes=3) as pool:
        res = pool.apply_async(func=work, args=['A'])
        x = res.get(timeout=1)
        print(x)
    print(f'Fin on pid={os.getpid()}')
