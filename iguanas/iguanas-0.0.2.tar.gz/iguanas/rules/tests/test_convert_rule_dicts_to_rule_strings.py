import pytest
from iguanas.rules._convert_rule_dicts_to_rule_strings import _ConvertRuleDictsToRuleStrings
import pandas as pd
import numpy as np


@pytest.fixture
def _data():
    np.random.seed(0)
    X = pd.DataFrame(
        {
            'A': np.random.uniform(0, 100, 100),
            'B': ['foo', 'bar'] * 50,
            'C': [1.0, 2.0, 3.0, np.nan] * 25,
            'D': ['foo', 'bar', np.nan, 'no'] * 25,
            'E': [1.0, 2.0, 3.0, 4.0] * 25,
            'F': [1.0, 2.0, 3.0, 5.0] * 25,
            'G': ['foo', '', np.nan, ''] * 25,

        }
    )
    return X


@pytest.fixture
def _rule_dict():
    rule_dict = {'condition': 'AND',
                 'rules': [{'condition': 'OR',
                            'rules': [{'field': 'A',
                                       'operator': 'greater_or_equal',
                                       'value': 60.0},
                                      {'field': 'B',
                                       'operator': 'begins_with',
                                       'value': 'foo'},
                                      {'field': 'C',
                                       'operator': 'is_null',
                                       'value': None}]},
                           {'field': 'D',
                            'operator': 'in', 'value': ['foo', 'bar']},
                           {'field': 'E',
                            'operator': 'equal_field',
                            'value': 'F'},
                           {'field': 'G',
                            'operator': 'is_empty',
                            'value': None}
                           ]
                 }
    return rule_dict


@pytest.fixture
def _rule_strings():
    rule_strings = {
        False: "((X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))&(X['D'].isin(['foo', 'bar']))&(X['E']==X['F'])&(X['G'].fillna('')=='')",
        True: "((X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))&(X['D'].isin(['foo', 'bar']))&(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))&(X['G'].fillna('')=='')"
    }
    return rule_strings


@pytest.fixture
def _expected_rule_lists():
    expected_results = {
        False: ["((X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))",
                "(X['D'].isin(['foo', 'bar']))",
                "(X['E']==X['F'])",
                "(X['G'].fillna('')=='')"],
        True: ["((X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))",
               "(X['D'].isin(['foo', 'bar']))",
               "(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))",
               "(X['G'].fillna('')=='')"]
    }
    return expected_results


@pytest.fixture
def _expected_rule_lists_as_lambda_True():
    expected_results = {
        (False, True): ["((X['A']>={A})|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))",
                        "(X['D'].isin(['foo', 'bar']))",
                        "(X['E']==X['F'])",
                        "(X['G'].fillna('')=='')"],
        (False, False): ["((X['A']>={})|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))",
                         "(X['D'].isin(['foo', 'bar']))",
                         "(X['E']==X['F'])",
                         "(X['G'].fillna('')=='')"],
        (True, True): ["((X['A'].to_numpy(na_value=np.nan)>={A})|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))",
                       "(X['D'].isin(['foo', 'bar']))",
                       "(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))",
                       "(X['G'].fillna('')=='')"],
        (True, False): ["((X['A'].to_numpy(na_value=np.nan)>={})|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))",
                        "(X['D'].isin(['foo', 'bar']))",
                        "(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))",
                        "(X['G'].fillna('')=='')"]
    }

    return expected_results


def test_convert(_rule_dict, _rule_strings, _data):
    expected_rule_strings = _rule_strings
    X = _data
    rule_dict = _rule_dict
    rule_dicts = {}
    rule_dicts['Rule1'] = rule_dict
    r = _ConvertRuleDictsToRuleStrings(rule_dicts=rule_dicts)
    for as_numpy, expected_rule_string in expected_rule_strings.items():
        rule_string = r.convert(as_numpy=as_numpy)
        assert rule_string['Rule1'] == expected_rule_string
        X_rule = eval(rule_string['Rule1'])
        assert X_rule.sum() == 11


def test_convert_rule(_rule_dict, _rule_strings, _data):
    expected_rule_strings = _rule_strings
    X = _data
    rule_dict = _rule_dict
    for as_numpy, expected_rule_string in expected_rule_strings.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        rule_string = r._convert_rule(rule_dict=rule_dict, as_numpy=as_numpy)
        assert rule_string == expected_rule_string
        X_rule = eval(rule_string)
        assert X_rule.sum() == 11


def test_recurse_convert_rule_dict_conditions_as_lambda_False(_rule_strings, _rule_dict):
    expected_rule_strings = _rule_strings
    rule_dict = _rule_dict
    for as_numpy, expected_rule_string in expected_rule_strings.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        rule_string = r._recurse_convert_rule_dict_conditions(rule_dict=rule_dict,
                                                              as_numpy=as_numpy,
                                                              as_lambda=False,
                                                              with_kwargs=None)
        assert rule_string == f'({expected_rule_string})'


def test_recurse_convert_rule_dict_conditions_as_lambda_True(_rule_strings, _rule_dict):
    rule_dict = _rule_dict
    expected_rule_strings = _rule_strings
    rule_string_pandas = f'({expected_rule_strings[False]})'
    rule_string_numpy = f'({expected_rule_strings[True]})'
    expected_results = {
        (False, True): rule_string_pandas,
        (False, False): rule_string_pandas,
        (True, True): rule_string_numpy,
        (True, False): rule_string_numpy,
    }
    for (as_numpy, with_kwargs), expected_rule_string in expected_results.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        rule_lambda_string = r._recurse_convert_rule_dict_conditions(rule_dict=rule_dict,
                                                                     as_numpy=as_numpy,
                                                                     as_lambda=True,
                                                                     with_kwargs=with_kwargs)
        if with_kwargs:
            rule_lambda = lambda **kwargs: rule_lambda_string.format(**kwargs)
            assert rule_lambda(**r._lambda_kwargs) == expected_rule_string
        else:
            rule_lambda = lambda *args: rule_lambda_string.format(*args)
            assert rule_lambda(*r._lambda_args) == expected_rule_string


def test_convert_rule_dict_conditions_as_lambda_False(_expected_rule_lists, _rule_dict):
    expected_rule_lists = _expected_rule_lists
    rule_dict = _rule_dict
    rules_list = rule_dict['rules']
    for as_numpy, expected_rule_list in expected_rule_lists.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        rule_list = r._convert_rule_dict_conditions(
            rules_list=rules_list, as_numpy=as_numpy, as_lambda=False, with_kwargs=None)
        assert rule_list == expected_rule_list


def test_convert_rule_dict_conditions_as_lambda_True(_expected_rule_lists_as_lambda_True, _rule_dict):
    expected_rule_lists = _expected_rule_lists_as_lambda_True
    rule_dict = _rule_dict
    rules_list = rule_dict['rules']
    for (as_numpy, with_kwargs), expected_rule_list in expected_rule_lists.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        rule_list = r._convert_rule_dict_conditions(
            rules_list=rules_list, as_numpy=as_numpy, as_lambda=True, with_kwargs=with_kwargs)
        assert rule_list == expected_rule_list


def test_create_condition_string_from_dict():
    condition_dict = {'field': 'A',
                      'operator': 'greater_or_equal',
                      'value': 60.0}
    expected_strings = {
        (False, False, False): "(X['A']>=60.0)",
        (False, True, True): "(X['A']>={A})",
        (False, True, False): "(X['A']>={})",
        (True, False, False): "(X['A'].to_numpy(na_value=np.nan)>=60.0)",
        (True, True, True): "(X['A'].to_numpy(na_value=np.nan)>={A})",
        (True, True, False): "(X['A'].to_numpy(na_value=np.nan)>={})"
    }
    for (as_numpy, as_lambda, with_kwargs), expected_string in expected_strings.items():
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        condition_string = r._create_condition_string_from_dict(condition_dict=condition_dict,
                                                                as_numpy=as_numpy,
                                                                as_lambda=as_lambda,
                                                                with_kwargs=with_kwargs)
        assert condition_string == expected_string


def test_parse_value_lambda():
    condition_dict1 = {
        'field': 'A',
        'operator': 'greater_or_equal',
        'value': 60.0
    }
    condition_dict2 = {
        'field': 'A',
        'operator': 'less',
        'value': 100.0
    }
    condition_dict3 = {
        'field': 'A',
        'operator': 'is',
        'value': None
    }
    condition_dict4 = {
        'field': 'A',
        'operator': 'contains',
        'value': 'james'
    }
    expected_results = {
        True: ('{A}', '{A%0}', [], [], {'A': 60.0, 'A%0': 100.0}),
        False: ('{}', '{}', ['A', 'A'], [60.0, 100.0], {})
    }
    for with_kwargs in [True, False]:
        r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
        value = r._parse_value_lambda(
            condition_dict=condition_dict1, field='A', with_kwargs=with_kwargs
        )
        assert value == expected_results[with_kwargs][0]
        value = r._parse_value_lambda(
            condition_dict=condition_dict2, field='A', with_kwargs=with_kwargs
        )
        assert value == expected_results[with_kwargs][1]
        assert r._rule_features == expected_results[with_kwargs][2]
        assert r._lambda_args == expected_results[with_kwargs][3]
        assert r._lambda_kwargs == expected_results[with_kwargs][4]
    value = r._parse_value_lambda(
        condition_dict=condition_dict3, field='A', with_kwargs=True
    )
    assert value is None
    value = r._parse_value_lambda(
        condition_dict=condition_dict4, field='A', with_kwargs=True
    )
    assert value == "'{A}'"


def test_parse_value_string():
    condition_dicts = [({'value': 1}, 1), ({'value': 'A'}, "'A'")]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for condition_dict, expected_result in condition_dicts:
        value = r._parse_value_string(condition_dict=condition_dict)
        assert value == expected_result


def test_create_condition_string_for_str_based_operators():
    inputs = [
        ('A', "'foo'", 'startswith', None, False),
        ('A', "'foo'", 'startswith', None, True),
    ]
    expected_results = [
        "(X['A'].str.startswith('foo', na=False))",
        "(~X['A'].str.startswith('foo', na=False))"
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_str_based_operators(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_contains_operator():
    inputs = [
        ('A', "'foo'", 'contains', None, False),
        ('A', "'foo'", 'contains', None, True),
    ]
    expected_results = [
        "(X['A'].str.contains('foo', na=False, regex=False))",
        "(~X['A'].str.contains('foo', na=False, regex=False))"
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_contains_operator(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_is_in_operator():
    inputs = [
        ('A', ['foo', 'bar'], 'isin', None, False),
        ('A', ['foo', 'bar'], 'isin', None, True),
    ]
    expected_results = [
        "(X['A'].isin(['foo', 'bar']))",
        "(~X['A'].isin(['foo', 'bar']))"
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_is_in_operator(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_is_null_operator():
    inputs = [
        ('A', None, 'isna', True, False),
        ('A', None, 'isna', True, True),
        ('A', None, 'isna', False, False),
        ('A', None, 'isna', False, True),
    ]
    expected_results = [
        "(pd.isna(X['A'].to_numpy(na_value=np.nan)))",
        "(~pd.isna(X['A'].to_numpy(na_value=np.nan)))",
        "(X['A'].isna())",
        "(~X['A'].isna())"
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_is_null_operator(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_standard_operators():
    inputs = [
        ('A', 3, ">=", True, None),
        ('A', 3, ">=", False, None),
    ]
    expected_results = [
        "(X['A'].to_numpy(na_value=np.nan)>=3)",
        "(X['A']>=3)",
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_standard_operators(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_field_level_comparison():
    inputs = [
        ('A', "'B'", "==", True, None),
        ('A', "'B'", "==", False, None),
    ]
    expected_results = [
        "(X['A'].to_numpy(na_value=np.nan)==X['B'].to_numpy(na_value=np.nan))",
        "(X['A']==X['B'])",
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_field_level_comparison(
            *args)
        assert condition_string == expected_result


def test_create_condition_string_for_is_empty_operator():
    inputs = [
        ('A', None, "fillna('')==", None, True),
        ('A', None, "fillna('')==", None, False)
    ]
    expected_results = [
        "(~X['A'].fillna('')=='')",
        "(X['A'].fillna('')=='')"
    ]
    r = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    for args, expected_result in zip(inputs, expected_results):
        condition_string = r._create_condition_string_for_is_empty_operator(
            *args)
        assert condition_string == expected_result


def test_errors():
    condition_dict = {
        'field': 'name',
        'operator': 'is_like',
        'value': 'james'
    }
    c = _ConvertRuleDictsToRuleStrings(rule_dicts={})
    with pytest.raises(Exception, match='Operator not currently supported in Iguanas. Rule cannot be parsed.'):
        c._create_condition_string_from_dict(
            condition_dict=condition_dict, as_numpy=False, as_lambda=False,
            with_kwargs=False
        )
