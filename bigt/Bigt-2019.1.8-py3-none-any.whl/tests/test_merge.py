
from bigt.dictext import DictExt

def test_merge_simple():
    a = {"a":[{'1': '1', '2': '2'},{'1': '1', '2': '2'}]}
    b = {"a":[{'1': '1', '2': '2'},{'3': '3', '2': '2'}]}
    #assert DictExt(a, b)['a'][0] == {'1': '1', '2': '2', '3': '3'}
    m = DictExt(a) + DictExt(b)
    assert m['a'][1] == DictExt({'1': '1', '2': '2', '3': '3'})

def test_merge_dict_in_dict():
    a = {"a":{'1': '1', '3': '3'}}
    b = {"a":{'1': '1', '2': '2'}}
    assert (DictExt(a) + DictExt(b))['a'] == DictExt({'1': '1', '2': '2', '3': '3'})

def test_merge_nested_dict_in_dict():
    a = {"a":{'1': {"1": 1}}}
    b = {"a":{'1': {"2": 2}}}
    assert (DictExt(a) + DictExt(b))['a']['1'] == DictExt({'1': 1, '2': 2})

def test_merge_dict_with_bool():
    a = {"a":False}
    b = {"a":True}
    assert (DictExt(a) + DictExt(b))['a']
    
def test_merge_diff_lists_size():
    a = {"a":['1', '2']}
    b = {"a":['1', '2', '3']}
    assert (DictExt(a) + DictExt(b))['a'] == ['1', '2', '3']

def test_merge_diff_types():
    a = {"a": False}
    b = {"a":"True"}
    assert (DictExt(a) + DictExt(b))['a'] == True
    
def test_merge_float():
    a = {"a": 1.2}
    b = {"a": 1.3}
    assert (DictExt(a) + DictExt(b))['a'] == 1.3

def test_merge_dict_with_list_with_str():
    a = {"a":['1', '2']}
    b = {"a":['1', '3']}
    assert (DictExt(a) + DictExt(b))['a'] == ["1", "2", "3"]

def test_merge_negative_case_dict_to_list():
    a = {"a":{'1': '1', '3': '3'}}
    b = {"a":['1', '2']}
    try:
        DictExt(a) + DictExt(b)
        assert False
    except:
        pass

def test_merge_negative_case_nested_list():
    a = {"a":[['1', '3']]}
    b = {"a":[['1', '2']]}
    try:
        DictExt(a) + DictExt(b)
        assert False
    except:
        pass

def test_merge_negative_not_supported_type():
    class NOT_SUPPORTED_TYPE:
        pass
    a = {"a": NOT_SUPPORTED_TYPE()}
    b = {"a": NOT_SUPPORTED_TYPE()}
    try:
        DictExt(a).merge(DictExt(b))
        assert False
    except:
        pass