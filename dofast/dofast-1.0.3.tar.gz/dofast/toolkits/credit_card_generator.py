# Eli Fulkerson
# http://www.elifulkerson.com

import random
import sys
from typing import Generator, List, Tuple


class Luhn:
    '''Luhn Algorithm'''
    @staticmethod
    def double(digit: int) -> int:
        '''Double digit, add its digits together if they are >= 10,
        e.g., 18 => 1 + 8 => 9
        '''
        xn = digit * 2
        return xn if xn < 10 else xn - 9

    @staticmethod
    def validate(cc_number: List[int]) -> bool:
        '''Validate when a given cc number (string) passes mod10 check.
        1. Starting from the rightmost digit, double the value of every second digit.
        2. If doubling of a number results in a two digit number, i.e., greater than 9 
            (e.g., 6 × 2 = 12), then add the digits of the product (e.g., 12: 1 + 2 = 3, 15: 1 + 5 = 6), 
            to get a single digit number. 
        3. If the total modulo 10 is equal to 0 (if the total ends in zero) then 
            the number is valid according to the Luhn formula; else it is not valid.
        '''
        xn = sum(
            Luhn.double(e) if i % 2 else e
            for i, e in enumerate(cc_number[::-1]))
        return (xn % 10) == 0


def rand_int(left: int, right: int) -> int:
    '''Generate a random number within the range [left, right]'''
    assert left <= right, "Illegae range [{}, {}]".format(left, right)
    return random.randint(left, right)


def generate_credit_number(prefix: str, length: int) -> str:
    '''Generate a random number starting with prefix and with 
    length "length" that passes mod10'''

    while True:
        cc = [rand_int(0, 9) if c.lower() == 'x' else int(c) for c in prefix]
        cc += [rand_int(0, 9) for _ in range(length - len(cc))]
        if Luhn.validate(cc):
            return ''.join(map(str, cc))


def generate_date() -> Tuple[int, int]:
    m = rand_int(1, 12)
    y = rand_int(2023, 2029)
    return m, y


def create_cc_numbers(prefix: str = '537630',
                      count: int = 10,
                      ccnumber_length: int = 16) -> Generator:
    "Print count numbers that pass mod10 - example function"
    for _ in range(count):
        cc = generate_credit_number(prefix, ccnumber_length)
        yield cc


if __name__ == '__main__':
    prefix = sys.argv[1] if len(sys.argv) > 1 else '537630'
    ccnumber_length = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    numbers = create_cc_numbers(prefix, 10, ccnumber_length)
    for n in numbers:
        print(n)
