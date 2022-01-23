from gregorian_months import get_number
import pytest


def test_months():
    assert 1 == get_number("January"), "Should be 1"
    assert 2 == get_number("February"), "Should be 2"
    assert 3 == get_number("March"), "Should be 3"
    assert 4 == get_number("April"), "Should be 4"
    assert 5 == get_number("May"), "Should be 5"
    assert 6 == get_number("June"), "Should be 6"
    assert 7 == get_number("July"), "Should be 7"
    assert 8 == get_number("August"), "Should be 8"
    assert 9 == get_number("September"), "Should be 9"
    assert 10 == get_number("October"), "Should be 10"
    assert 11 == get_number("November"), "Should be 11"
    assert 12 == get_number("December"), "Should be 12"


def test_uppercased_months():
    assert 1 == get_number("JANUARY"), "Should be 1"
    assert 2 == get_number("FEBRUARY"), "Should be 2"
    assert 3 == get_number("MARCH"), "Should be 3"
    assert 4 == get_number("APRIL"), "Should be 4"
    assert 5 == get_number("MAY"), "Should be 5"
    assert 6 == get_number("JUNE"), "Should be 6"
    assert 7 == get_number("JULY"), "Should be 7"
    assert 8 == get_number("AUGUST"), "Should be 8"
    assert 9 == get_number("SEPTEMBER"), "Should be 9"
    assert 10 == get_number("OCTOBER"), "Should be 10"
    assert 11 == get_number("NOVEMBER"), "Should be 11"
    assert 12 == get_number("DECEMBER"), "Should be 12"


def test_lowercased_months():
    assert 1 == get_number("january"), "Should be 1"
    assert 2 == get_number("february"), "Should be 2"
    assert 3 == get_number("march"), "Should be 3"
    assert 4 == get_number("april"), "Should be 4"
    assert 5 == get_number("may"), "Should be 5"
    assert 6 == get_number("june"), "Should be 6"
    assert 7 == get_number("july"), "Should be 7"
    assert 8 == get_number("august"), "Should be 8"
    assert 9 == get_number("september"), "Should be 9"
    assert 10 == get_number("october"), "Should be 10"
    assert 11 == get_number("november"), "Should be 11"
    assert 12 == get_number("december"), "Should be 12"


def test_random_cased_months():
    assert 1 == get_number("jAnUarY"), "Should be 1"
    assert 2 == get_number("FEbRuarY"), "Should be 2"
    assert 3 == get_number("mArcH"), "Should be 3"
    assert 4 == get_number("aPRiL"), "Should be 4"
    assert 5 == get_number("maY"), "Should be 5"
    assert 6 == get_number("juNe"), "Should be 6"
    assert 7 == get_number("jULy"), "Should be 7"
    assert 8 == get_number("auGuSt"), "Should be 8"
    assert 9 == get_number("sepTeMBEr"), "Should be 9"
    assert 10 == get_number("OcTObER"), "Should be 10"
    assert 11 == get_number("noVEmBEr"), "Should be 11"
    assert 12 == get_number("DeCemBEr"), "Should be 12"


def test_errors():
    with pytest.raises(TypeError):
        get_number(1)

    with pytest.raises(ValueError):
        get_number("ErrorMonth")
