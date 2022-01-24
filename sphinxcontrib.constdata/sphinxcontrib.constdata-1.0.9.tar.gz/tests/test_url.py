import pytest

from sphinxcontrib.constdata.url import Url
from sphinxcontrib.constdata.utils import ConstdataError


def test_keep_id_in_qs():
    """If QS contains the single item with blank value, it's ID."""
    assert "someId" == Url("foo.csv?someId").get_id()
    assert "someId" == Url("path/to/foo.csv?someId").get_id()


def test_error_if_invalid_qs():
    with pytest.raises(ConstdataError):
        Url("foo.csv").get_id()

    with pytest.raises(ConstdataError):
        Url("foo.csv?too=many&params=are&also=invalid").get_id()

    with pytest.raises(ConstdataError):
        Url("foo.csv#fragmentOnly").get_id()


def test_get_rel_path():
    assert "foo.csv" == Url("foo.csv").get_rel_path()
    assert "foo.csv" == Url("foo.csv?qs").get_rel_path()
    assert "path/to/foo.csv" == Url("path/to/foo.csv?id").get_rel_path()
