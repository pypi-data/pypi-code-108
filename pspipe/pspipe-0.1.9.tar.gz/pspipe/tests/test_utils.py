from pspipe import utils


def test_alphanum():
    assert utils.alphanum('|sd dd 12.s ') == 'sddd12s'


def test_all_same():
    assert utils.all_same([1, 1, 1])
    assert not utils.all_same([1, 1, 2])
    assert not utils.all_same([1, 2, 1])
    assert utils.all_same(['a', 'a', 'a'])
    assert not utils.all_same(['a', 'a', 'a', 1])


def test_all_in_other():
    assert utils.all_in_other([1, 2], list(range(10)))
    assert not utils.all_in_other([1, 2, 10], list(range(10)))


def test_is_in_lst_bin():
    assert utils.is_in_lst_bin(2, 1, 3)
    assert utils.is_in_lst_bin(2, 2, 3)
    assert not utils.is_in_lst_bin(2, 3, 3)
    assert not utils.is_in_lst_bin(3, 2, 3)
    assert not utils.is_in_lst_bin(3, 21, 3)
    assert utils.is_in_lst_bin(2, 21, 3)
    assert utils.is_in_lst_bin(21, 21, 3)
