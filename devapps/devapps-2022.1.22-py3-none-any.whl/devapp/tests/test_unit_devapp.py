# adding builtins


def test_dict_tree():
    a = {'foo': {'bar': 'baz'}}
    d = DT(a)
    assert isinstance(a, dict)
    assert d.foo.bar == 'baz'
    assert d.foo['bar'] == 'baz'


def test_dict_tree_matched():
    a = {'foo': {'bar': 'baz'}}
    d = T(a)
    assert isinstance(a, dict)
    assert d.foo.bar == 'baz'
    assert d.foo['bar'] == 'baz'
    assert isinstance(a, dict)
    assert d.f.ba == 'baz'
    assert d.fo['bar'] == 'baz'
