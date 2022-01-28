import concurrent.futures
from typing import Callable
import time
from pprint import pprint


def multithread(function: Callable, switch_ips: list[str]) -> None:
    """
    Runs function concurrently on list of switch IP
    addresses. TODO: Fix messy output when running functions concurrently.
    :param function: Function to run on IPs
    :param switch_ips: List of switch IP addresses
    :return: None
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        start = time.perf_counter()
        response_process = []
        for ip in switch_ips:
            response_process.append(executor.submit(function, ip))
        print(f'Duration: {time.perf_counter() - start}')
        for f in response_process[0:]:
            pprint(f.result())


if __name__ == '__main__':
    pass
