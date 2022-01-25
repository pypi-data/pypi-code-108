import pytest

from niota.encoder import hexstr_to_str, str_to_hexstr


@pytest.fixture
def str_hextstr_pair_fixture():
    return ('NumbersProtocol', '4e756d6265727350726f746f636f6c')


@pytest.mark.unit
def test_hexstr_to_str(str_hextstr_pair_fixture):
    assert hexstr_to_str(str_hextstr_pair_fixture[1]) == str_hextstr_pair_fixture[0]


@pytest.mark.unit
def test_str_to_hexstr(str_hextstr_pair_fixture):
    assert str_to_hexstr(str_hextstr_pair_fixture[0]) == str_hextstr_pair_fixture[1]
