import random

from fakelish import fakelish


def test_generate_fake_word_with_unexpected_length():
    random.seed(42)
    assert fakelish.generate_fake_word_with_unexpected_length() == "umpic"


def test_generate_fake_word_by_length():
    random.seed(4242)
    assert fakelish.generate_fake_word_by_length(10) == "bieweerbre"


def test_generate_fake_word():
    random.seed(424242)
    assert fakelish.generate_fake_word(4, 11) == "burfus"
