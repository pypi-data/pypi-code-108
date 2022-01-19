from bigt.dictext import DictExt

def test_simple():
    assert DictExt({"a": 1, "b": 2}) == DictExt({"a": 1, "b": 2})

def test_nested():
    assert DictExt({"a": {"a": 1}}) == DictExt({"a": {"a": 1}})

def test_different_order():
    assert DictExt({"a": 1, "b": 2}) == DictExt({"b": 2, "a": 1})
    assert DictExt({"b": 2, "a": 1}) == DictExt({"a": 1, "b": 2})
    
def test_with_list():
    assert DictExt({"a": [1, 1, 3]}) == DictExt({"a": [3, 1, 1]})

def test_not_equel():
    assert DictExt({"a": "1"}) != DictExt({"a": 1})