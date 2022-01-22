import sys

from levo_commons.utils import syspath_prepend


def test_syspath_prepend():
    path = "./foo"
    assert path not in sys.path
    with syspath_prepend(path):
        assert sys.path[0] == path
    assert path not in sys.path


def test_syspath_prepend_nested():
    path_1 = "./foo"
    path_2 = "./bar"
    assert path_1 not in sys.path
    assert path_2 not in sys.path
    with syspath_prepend(path_1):
        assert sys.path[0] == path_1
        with syspath_prepend(path_2):
            assert sys.path[0] == path_2
            assert sys.path[1] == path_1
        assert sys.path[0] == path_1
    assert path_1 not in sys.path
    assert path_2 not in sys.path
