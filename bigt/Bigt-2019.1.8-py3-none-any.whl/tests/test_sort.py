from bigt.dictext import DictExt

def test_simple():
    assert DictExt({"aa": 3, "a": 1, "b": 2}) == DictExt({"b": 2, "a": 1, "aa": 3})

def test_nested():
    assert DictExt({"aa": 3, "a": [[3,1,8,5], {"b": {"bv": 1, "bc": 2}, "a": 1}]}) == \
        DictExt({"a": [{"a": 1, "b": {"bc": 2, "bv": 1}}, [1,3,5,8]], "aa": 3})