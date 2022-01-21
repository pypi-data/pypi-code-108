import pytest

from nexusmaker import CognateParser


def test_is_unique_cognateset():
    assert CognateParser().is_unique_cognateset('u_1')
    assert CognateParser().is_unique_cognateset('u_1', labelled=False)
    assert not CognateParser().is_unique_cognateset('hand_u_1', labelled=False)
    assert CognateParser().is_unique_cognateset('hand_u_1', labelled=True)


def test_simple():
    assert CognateParser().parse_cognate('1') == ['1']
    assert CognateParser().parse_cognate('10') == ['10']
    assert CognateParser().parse_cognate('100') == ['100']
    assert CognateParser().parse_cognate('111') == ['111']
    assert CognateParser().parse_cognate('1,2') == ['1', '2']
    assert CognateParser().parse_cognate('1   ,   2') == ['1', '2']


def test_dubious():
    assert CognateParser(uniques=True).parse_cognate('1?') == ['u_1']
    assert CognateParser(uniques=True).parse_cognate('?') == ['u_1']
    assert CognateParser(uniques=True).parse_cognate('1, 2?') == ['1']
    assert CognateParser(uniques=True).parse_cognate('1?, 2') == ['2']
    assert CognateParser(uniques=True).parse_cognate('91?, 42') == ['42']
    assert CognateParser(uniques=True).parse_cognate('?, 31') == ['31']
    # note that both of these are dubious, should become a unique
    # state instead
    assert CognateParser(uniques=True).parse_cognate('1?, 2?') == ['u_1']

    # check these are removed when uniques are false
    assert CognateParser(uniques=False).parse_cognate('1?') == []
    assert CognateParser(uniques=False).parse_cognate('?') == []


def test_bad_entries():
    # coded as x
    assert CognateParser(uniques=True).parse_cognate('X') == ['u_1']
    assert CognateParser(uniques=True).parse_cognate('x') == ['u_1']
    assert CognateParser(uniques=True).parse_cognate('X20') == ['u_1']
    assert CognateParser(uniques=True).parse_cognate('x20') == ['u_1']

    # entries that are in the wrong word (e.g. you sg. not you pl.)
    assert CognateParser(uniques=True).parse_cognate('s') == ['u_1']

    # remove when uniques is False
    assert CognateParser(uniques=False).parse_cognate('X') == []
    assert CognateParser(uniques=False).parse_cognate('x') == []
    assert CognateParser(uniques=False).parse_cognate('s') == []


def test_uniques():
    CP = CognateParser()
    assert CP.parse_cognate('') == ['u_1']
    assert CP.parse_cognate('') == ['u_2']
    assert CP.parse_cognate('') == ['u_3']
    assert CP.parse_cognate('') == ['u_4']
    assert CP.parse_cognate(None) == ['u_5']

    CP = CognateParser(uniques=False)
    assert CP.parse_cognate('') == []
    assert CP.parse_cognate('') == []
    assert CP.parse_cognate(None) == []


def test_strict_off():
    # when strict is set to false, dubious entries survive.
    assert CognateParser(strict=False).parse_cognate('1?') == ['1']
    assert CognateParser(strict=False).parse_cognate('1, 2?') == ['1', '2']


def test_complicated_strict_unique():
    CP = CognateParser(strict=True, uniques=True)
    # # 3. right
    # Maori    katau         5, 40
    # Maori    matau         5
    # South Island Maori    tika
    assert CP.parse_cognate('5, 40') == ['5', '40']
    assert CP.parse_cognate('5') == ['5']
    assert CP.parse_cognate('') == ['u_1']

    # # 8. turn
    # Maori    huri         15
    # South Island Maori    tahuli         15
    # South Island Maori    tahuri    to turn, to turn around    15
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']

    # # 20. to know
    # Maori    moohio         52
    # South Island Maori    matau         1
    # South Island Maori    mohio    to know    52
    # South Island Maori    ara    to know, to awake
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('1') == ['1']
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('') == ["u_2"]

    # # 36: to spit
    # Maori    tuha         19, 34?
    # South Island Maori    huare         18
    # South Island Maori    tuha    to expectorate, to spit    19, 34?
    assert CP.parse_cognate('19, 34?') == ['19']
    assert CP.parse_cognate('18') == ['18']
    assert CP.parse_cognate('19, 34?') == ['19']


def test_complicated_nostrict_unique():
    CP = CognateParser(strict=False, uniques=True)
    # # 3. right
    # Maori    katau         5, 40
    # Maori    matau         5
    # South Island Maori    tika
    assert CP.parse_cognate('5, 40') == ['5', '40']
    assert CP.parse_cognate('5') == ['5']
    assert CP.parse_cognate('') == ['u_1']

    # # 8. turn
    # Maori    huri         15
    # South Island Maori    tahuli         15
    # South Island Maori    tahuri    to turn, to turn around    15
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']

    # # 20. to know
    # Maori    moohio         52
    # South Island Maori    matau         1
    # South Island Maori    mohio    to know    52
    # South Island Maori    ara    to know, to awake
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('1') == ['1']
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('') == ["u_2"]

    # # 36: to spit
    # Maori    tuha         19, 34?
    # South Island Maori    huare         18
    # South Island Maori    tuha    to expectorate, to spit    19, 34?
    assert CP.parse_cognate('19, 34?') == ['19', '34']
    assert CP.parse_cognate('18') == ['18']
    assert CP.parse_cognate('19, 34?') == ['19', '34']


def test_complicated_nostrict_nounique():
    CP = CognateParser(strict=False, uniques=False)
    # # 3. right
    # Maori    katau         5, 40
    # Maori    matau         5
    # South Island Maori    tika
    assert CP.parse_cognate('5, 40') == ['5', '40']
    assert CP.parse_cognate('5') == ['5']
    assert CP.parse_cognate('') == []

    # # 8. turn
    # Maori    huri         15
    # South Island Maori    tahuli         15
    # South Island Maori    tahuri    to turn, to turn around    15
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']
    assert CP.parse_cognate('15') == ['15']

    # # 20. to know
    # Maori    moohio         52
    # South Island Maori    matau         1
    # South Island Maori    mohio    to know    52
    # South Island Maori    ara    to know, to awake
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('1') == ['1']
    assert CP.parse_cognate('52') == ['52']
    assert CP.parse_cognate('') == []

    # # 36: to spit
    # Maori    tuha         19, 34?
    # South Island Maori    huare         18
    # South Island Maori    tuha    to expectorate, to spit    19, 34?
    assert CP.parse_cognate('19, 34?') == ['19', '34']
    assert CP.parse_cognate('18') == ['18']
    assert CP.parse_cognate('19, 34?') == ['19', '34']


def test_complicated_with_slash():
    assert CognateParser(strict=True, uniques=True).parse_cognate('53/54') == ['53', '54']


def test_combined_cognate():
    assert CognateParser().parse_cognate('1a') == ['1', '1a']
    assert CognateParser().parse_cognate('2b') == ['2', '2b']
    assert CognateParser().parse_cognate('3az') == ['3', '3az']
    assert CognateParser().parse_cognate('45c') == ['45', '45c']
    assert CognateParser().parse_cognate('1a,2b') == ['1', '1a', '2', '2b']


def test_sorting():
    assert CognateParser(sort=True).parse_cognate('2, 1') == ['1', '2']
    assert CognateParser(sort=False).parse_cognate('2, 1') == ['2', '1']


# unparsable cognate sets raise ValueErrors
def test_empty_entries():
    with pytest.raises(ValueError):
        CognateParser(uniques=False).parse_cognate(',,')


def test_bad_cog_int():
    with pytest.raises(ValueError):
        CognateParser().parse_cognate(1)


def test_trailing_dash():
    with pytest.raises(ValueError):
        CognateParser().parse_cognate('1-')


def test_semicolon():
    with pytest.raises(ValueError):
        CognateParser().parse_cognate('2, 63; 87')
