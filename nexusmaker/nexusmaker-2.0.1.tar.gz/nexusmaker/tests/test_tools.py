import pytest

from nexusmaker.tools import slugify, parse_parameter, natsort


def test_natural_sort():
    assert natsort(['b', 'a']) == ['a', 'b']
    assert natsort(['c', '1']) == ['1', 'c']
    assert natsort(['52', '1']) == ['1', '52']
    assert natsort(['54', '53']) == ['53', '54']
    assert natsort(['53', '54']) == ['53', '54']


def test_slugify():
    assert slugify('Banggai (W.dialect)') == 'Banggai_Wdialect'
    assert slugify('Aklanon - Bisayan') == 'Aklanon_Bisayan'
    assert slugify('Gimán') == 'Giman'
    assert slugify('Hanunóo') == 'Hanunoo'
    assert slugify('Kakiduge:n Ilongot') == 'Kakidugen_Ilongot'
    assert slugify('Angkola / Mandailin') == 'Angkola_Mandailin'
    assert slugify('V’ënen Taut') == 'Venen_Taut'


def test_parse_parameter():
    assert parse_parameter("One_1") == ("One", "1")
    assert parse_parameter("One_13") == ("One", "13")
    assert parse_parameter("One_u_21") == ("One", "u_21")
    assert parse_parameter("One_u21") == ("One", "u21")
    assert parse_parameter("One_Hundred_16") == ("One_Hundred", "16")
    assert parse_parameter("One_Hundred_u_16") == ("One_Hundred", "u_16")
    assert parse_parameter("One_Hundred_u16") == ("One_Hundred", "u16")
    assert parse_parameter("Eight_u_3569") == ("Eight", "u_3569")
    assert parse_parameter("Eight_u3569") == ("Eight", "u3569")
    assert parse_parameter("correct_true_u_5631") == ("correct_true", "u_5631")
    assert parse_parameter("correct_true_u5631") == ("correct_true", "u5631")
    assert parse_parameter("to_tie_up_fasten_u_5685") == ("to_tie_up_fasten", "u_5685")
    assert parse_parameter("to_tie_up_fasten_u5685") == ("to_tie_up_fasten", "u5685")

    with pytest.raises(ValueError):
        parse_parameter("hand")
