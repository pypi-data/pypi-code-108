# pylint: skip-file

import random
import string

import pytest

from ddna import DDNA
from helpers.utils import convert_to_bits, convert_to_string

ddna = DDNA()


def generate_random_strings():
    """
    Generates 100 random strings of length between 1 and 500.
    Example: rdF66~-C-!~!}8gh3;2aRL=b].(,K?GE.]"YEb)]M02H>gA
    Example: '1wWq;gRRXM1)rGMg1a$i2%>Zl]6Obx"K2v
    """
    for _ in range(100):
        yield ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(random.randint(1, 500)))


def generate_invalid_dna():
    """
    Generates 50 invalid dna sequences.
    eg: adasdsa 
    eg: ACTG1234
    eg: 32SDIk2...
    """
    for _ in range(50):
        yield "".join(random.choice(string.ascii_letters) for _ in range(random.randint(1, 500)))


# array of random strings
random_strings = list(generate_random_strings())


# Testing validity of the generated strings (OP)
@pytest.mark.parametrize("random_string", random_strings)
def test_random_string(random_string):
    """
    Test that the random string is a string.
    """
    assert isinstance(random_string, str)


# Converting strings to DNA Bases
dna_bases = [ddna.encode(random_string) for random_string in random_strings]

# converting dna_bases back to strings
strings = [ddna.decode(dna_base) for dna_base in dna_bases]

# loop throught the list of strings and compare them to the original strings using pytest.mark.parametrize


@pytest.mark.parametrize("random_string, dna_base, string", zip(random_strings, dna_bases, strings))
def test_convert_to_bits(random_string, dna_base, string):
    """
    Test that the converted DNA bases are equal to the original strings.
    """
    assert random_string == string


# loop through the list of random strings and convert them to bits
bits = [convert_to_bits(random_string) for random_string in random_strings]

# loop through the list of bits and convert them to strings
strings = [convert_to_string(bit) for bit in bits]

# loop through the list of strings and compare them to the original strings using pytest.mark.parametrize


@pytest.mark.parametrize("random_string, bit, string", zip(random_strings, bits, strings))
def test_convert_to_string(random_string, bit, string):
    """
    Test that the converted bits are equal to the original strings.
    """
    assert random_string == string


# Testing valid dna function
def test_valid_dna_1():
    """
    Test that the valid dna function returns True for valid dna sequences.
    """
    assert ddna.check_validity("ACGT")

# Testing invalid dna function using loop


@pytest.mark.parametrize("invalid_dna", generate_invalid_dna())
def test_invalid_dna_looped(invalid_dna):
    """
    Test that the invalid dna function returns False for invalid dna sequences.
    """
    assert not ddna.check_validity(invalid_dna)
