import json
from itertools import compress
import math
from typing import List

import nsq

from dofast.nsq.consumer import Consumer
from dofast.pipe import author
import codefast as cf
cf.logger.logname = '/tmp/consumer.log'
cf.logger.level = 'INFO'


class Primes:
    def half_sieve(self, n: int) -> List[int]:
        """
        Returns a list of prime numbers less than `n`.
        """
        if n <= 2:
            return []
        sieve = bytearray([True]) * (n // 2)
        for i in range(3, int(n**0.5) + 1, 2):
            if sieve[i // 2]:
                sieve[i * i // 2::i] = bytearray((n - i * i - 1) // (2 * i) +
                                                 1)
        primes = list(compress(range(1, n, 2), sieve))
        primes[0] = 2
        return primes

    def is_prime(self, n: int) -> bool:
        if n == 2:
            return True
        if n % 2 == 0 or n <= 1:
            return False
        sqr = int(math.sqrt(n)) + 1
        return all((n % divisor > 0 for divisor in range(3, sqr, 2)))


class CalculatePrime(Consumer):
    def __init__(self, topic: str, channel: str):
        SERVER_HOST = author.get('SERVER_HOST')
        self.worker = Primes()
        nsq.Reader(message_handler=self.async_handler,
                   nsqd_tcp_addresses=[f'{SERVER_HOST}:4150'],
                   topic=topic,
                   channel=channel,
                   max_in_flight=10,
                   lookupd_poll_interval=3)

    def consume(self, message: dict):
        msg = json.loads(message.body)
        cf.info('message received', msg)
        n = msg['number']
        if self.worker.is_prime(n):
            cf.info('{} is a prime'.format(n))
        else:
            cf.info('{} is NOT a prime'.format(n))
        return True


def calculate_prime():
    topic = 'primes'
    channel = 'calculate_prime'
    consumer = CalculatePrime(topic, channel)
    consumer.run()


if __name__ == '__main__':
    CalculatePrime('primes', 'calculate_prime').run()
