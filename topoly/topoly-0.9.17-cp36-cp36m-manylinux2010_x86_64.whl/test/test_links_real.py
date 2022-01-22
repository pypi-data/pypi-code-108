import pytest

from topoly import jones, yamada, kauffman_polynomial
from time import time
import logging

log = logging.getLogger()

algorithms_links = {'Jones': jones, 'Yamada': yamada, 'Kauffman Polynomial': kauffman_polynomial}

@pytest.mark.skip
def test_links_2lfk():
    for i in range(1000):
        results = {}
        for algorithm in algorithms_links.keys():
            print(str(i) + " calculating " + str(algorithm))
            t0 = time()
            results[algorithm] = algorithms_links[algorithm]('data/links/2lfk.xyz', tries=50, max_cross=25)
            time_elapsed = time() - t0
            print(str(i) + " Done " + str(algorithm) + ' ' + "in: " + str(round(time_elapsed, 3)))


if __name__ == '__main__':
    test_links_2lfk()
