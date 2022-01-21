import functools
from concurrent.futures  import ProcessPoolExecutor

import quickstats

def parallel_run(func, *iterables, max_workers=None):
    max_workers = max_workers or quickstats.MAX_WORKERS 

    with ProcessPoolExecutor(max_workers) as executor:
        result = executor.map(func, *iterables)

    return [i for i in result]