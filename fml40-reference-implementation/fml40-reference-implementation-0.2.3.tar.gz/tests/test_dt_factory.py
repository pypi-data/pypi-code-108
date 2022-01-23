import pprint
import re

from ml.dt_factory import DT_FACTORY, RE_NAMESPACE
from ml.feature import Feature
from ml.role import Role


def test_namespace_re():
    assert not RE_NAMESPACE.fullmatch("")
    assert not RE_NAMESPACE.fullmatch("a")
    assert not RE_NAMESPACE.fullmatch("2")
    assert not RE_NAMESPACE.fullmatch("a:b")
    assert not RE_NAMESPACE.fullmatch("1:b")
    assert not RE_NAMESPACE.fullmatch("b:1")
    assert RE_NAMESPACE.fullmatch("a::b")
    assert not RE_NAMESPACE.fullmatch("::b")
    assert not RE_NAMESPACE.fullmatch("a::")
    assert RE_NAMESPACE.fullmatch("ba::aa")
    assert not RE_NAMESPACE.fullmatch("b::a::a")
    assert not RE_NAMESPACE.fullmatch("b::a::1")


def test_class_instantiation():
    for key, s3i_class in DT_FACTORY.items():
        s3i_inst = s3i_class()
        assert RE_NAMESPACE.fullmatch(s3i_inst.class_name)
