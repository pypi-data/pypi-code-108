import pytest
from iguanas.rules._convert_rule_dicts_to_rule_lambdas import _ConvertRuleDictsToRuleLambdas
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
    rule_dict = {
        'Rule1':
        {'condition': 'AND',
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
         }}
    return rule_dict


@pytest.fixture
def _rule_strings():
    rule_strings = {
        (False, True): "((X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))&(X['D'].isin(['foo', 'bar']))&(X['E']==X['F'])&(X['G'].fillna('')=='')",
        (False, False): "((X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))&(X['D'].isin(['foo', 'bar']))&(X['E']==X['F'])&(X['G'].fillna('')=='')",
        (True, True): "((X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))&(X['D'].isin(['foo', 'bar']))&(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))&(X['G'].fillna('')=='')",
        (True, False): "((X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))&(X['D'].isin(['foo', 'bar']))&(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))&(X['G'].fillna('')=='')"
    }
    return rule_strings


def test_convert(_rule_dict, _rule_strings, _data):
    expected_rule_strings = _rule_strings
    X = _data
    rule_dict = _rule_dict
    r = _ConvertRuleDictsToRuleLambdas(rule_dicts=rule_dict)
    for (as_numpy, with_kwargs), expected_rule_string in expected_rule_strings.items():
        rule_lambdas = r.convert(as_numpy=as_numpy, with_kwargs=with_kwargs)
        rule_lambda = rule_lambdas['Rule1']
        if with_kwargs:
            rule_string = rule_lambda(**r.lambda_kwargs['Rule1'])
        else:
            rule_string = rule_lambda(*r.lambda_args['Rule1'])
        assert rule_string == expected_rule_string
        X_rule = eval(rule_string)
        assert X_rule.sum() == 11
