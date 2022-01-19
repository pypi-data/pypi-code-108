from bigt.dictext import DictExt, _str, _bool, _int, _list


def test_weights():
    a = {"a":[{'z': {'a': '21', 'b': False, 'd': '20'}}, {'z': {'a': '1', 'b': False, 'd': '2'}}]}
    b = {"a":[{'z': {'a': '1', 'b': False, 'd': '20', "y": 123}}]}
    result, not_present, changed = DictExt(b).issubset(a, weights={"a": {'z': {"a": 2, "y": {"v": 4}}}})
    assert not result
    assert not_present == {'a': [{'z': {'y': 123}}]}
    assert changed == {"a":[{'z': {'d': {"old": "20", "new": "2"}}}]}

def test_skip_path():
    a = {"a":[{'b': '1', 'c': {'a': '2'}},{'a': '1', 'b': '2'}]}
    b = {"a":[{'b': '10', 'c': {'a': '20'}},{'a': '1', 'b': '2'}]}
    result, not_present, changed = DictExt(a).issubset(b, skip=['a.c.a'])
    assert not result
    assert not not_present
    assert changed == {"a":[{'b': {"old": "1", "new": "10"}}]}

def test_skip_path_other_order():
    a = {"a":[{'b': '1', 'c': '2'},{'a': '1', 'b': '2'}]}
    b = {"a":[{'a': '1', 'b': '2'},{'b': '10', 'c': '20'}]}
    result, not_present, changed = DictExt(a).issubset(b, skip=['a.b'])
    assert not result
    assert not not_present
    assert changed == {"a":[{'c': {"old": "2", "new": "20"}}]}

def test_less_not_present_diff():
    a = {"a":[{'a': '1', 'd': '2'},{'b': '2', 'd': '20'}]}
    b = {"a":[{'b': '2', 'c': '20'},{'a': '1', 'd': '2'}]}
    result = DictExt(b) - DictExt(a)
    assert result == DictExt({"a":[{'c': '20'}]})

def test_full_diff():
    a = {"a":[{'a': '1', 'd': '2'},{'b': '2', 'dd': '20'}]}
    b = {"a":[{'bb': '2', 'cc': '20'},{'aa': '1', 'dd': '2'}]}
    _, not_present, _ = DictExt(b).issubset(a)
    assert not_present == DictExt(b)

def test_less_changed_diff():
    a = {"a":[{'a': '1', 'd': '2'},{'a': '21', 'd': '22'}]}
    b = {"a":[{'a': '1', 'd': '20'},{'a': '1', 'd': '2'}]}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert not not_present
    assert len(changed['a']) == 1
    assert len(changed['a'][0]) == 1, 'Found more diff than expected'
    assert changed['a'][0]['d']['old'] == '20'
    assert changed['a'][0]['d']['new'] == '2'

def test_issubset_regex_mask():
    a = {"a":[{'1': '1', '2': 'Test string to test 215 regex'},{'1': '1', '2': 'bla 2'}]}
    b = {"a":[{'1': '1', '2': r'test \d{3}'}, {'1': '1', '2': '^bl'}]}
    result, _, _ = DictExt(b).issubset(a, regex_mask=True)
    assert result

def test_issubset_regex_mask_off_swicher():
    a = {"a":[{'1': '1', '2': 'Test string to test 215 regex'}]}
    b = {"a":[{'1': '1', '2': 'test'}]}
    result, _, _ = DictExt(b).issubset(a)
    assert not result

def test_string_part():
    r, _, _ = _str().diff("test", "test")
    assert r
    r, _, _ = _str().diff("test", "not")
    assert not r

def test_bool_part():
    r, _, _ = _bool().diff(True, True)
    assert r
    r, _, _ = _bool().diff(False, False)
    assert r
    r, _, _ = _bool().diff(True, False)
    assert not r
    r, _, _ = _bool().diff(True, "1")
    assert r
    r, _, _ = _bool().diff(True, "yes")
    assert r
    r, _, _ = _bool().diff(False, "false")
    assert r

def test_int_part():
    r, _, _ = _int().diff(1, 1)
    assert r
    r, _, _ = _int().diff(2, 12)
    assert not r

def test_list_part():
    r, _, _ = _list().diff([1, 2], [2, 1])
    assert r
    r, _, _ = _list().diff([1, 2], [2, 3])
    assert not r

def test_simple_part():
    a = {"a": "str", "b": 123}
    b = {"a": "str", "b": 123}
    assert DictExt(a) >= DictExt(b)
    assert DictExt(b) <= DictExt(a)

def test_simple_diff_part():
    a = {"a": "str", "b": 321}
    b = {"a": "str1", "b": 123, "c": 12.1}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert changed == {
        "a": {"old": "str1", "new": "str"},
        "b": {"old": 123, "new": 321},
    }
    assert not_present == {"c": 12.1}

def test_simple_nested_dict_part():
    a = {"a": {"a": "str", "b": 123}}
    b = {"a": {"a": "str", "b": 1234}}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert changed == {
        "a": {"b": {"old": 1234, "new": 123} }
    }
    assert not not_present

def test_simple_list_in_dict_part():
    a = {"a": {"a": "str", "b": 123}}
    b = {"a": {"a": "str", "b": 1234}}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert changed == {
        "a": {"b": {"old": 1234, "new": 123} }
    }
    assert not not_present

def test_simple_not_present_dict_part():
    a = {"a": {"a": "str", "b": 123}}
    b = {"b": {"b": "str1", "c": 1234}}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert not changed
    assert not_present == b

def test_not_present_dict_part():
    a = {"a": [{"a": {"a": "str", "b": 123}}]}
    b = {"a": [{"b": {"b": "str1", "c": 1234}}]}
    result, not_present, changed = DictExt(b).issubset(a)
    assert not result
    assert not changed
    assert not_present == b

def test_not_present_dict_part_2():
    a = {"a": [{"a": {"a": "str", "b": 123}}, {"b": {"b": "str", "c": 123}}]}
    b = {"a": [{"b": {"b": "str", "c": 123}}]}
    result, not_present, changed = DictExt(a).issubset(b)
    assert not result
    assert not changed
    assert not_present == {"a": [{"a": {"a": "str", "b": 123}}]}

def test_compare_0_int():
    a = {"a": 0}
    b = {"a": 0}
    result, _, _ = DictExt(b).issubset(a)
    assert result

def test_compare_None():
    a = {"a": None, "b": 0}
    b = {"a": "", "b": None}
    result, _, _ = DictExt(b).issubset(a)
    assert result

def test_compare_None_with_dict():
    a = {"a": "str", "b": {"a": 0}}
    b = {"a": "str", "b": None}
    result, _, _ = DictExt(b).issubset(a)
    assert not result
    result, _, _ = DictExt(a).issubset(b)
    assert not result

def test_empty_lists():
    a = {"a": [[]]}
    b = {"a": [[]]}
    result, _, _ = DictExt(b).issubset(a)
    assert result

def test_compare_int_with_str():
    a = {"a":['1', 2]}
    b = {"a":[1, '2']}

    result, _, _ = DictExt(b).issubset(a)
    assert result


def test_get_pretty_key():
    a = DictExt({ "a": { 'b': 2 } })
    assert a.a.b == 2