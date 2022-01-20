import pytest
from iguanas.rules._convert_rule_strings_to_rule_dicts import _ConvertRuleStringsToRuleDicts


@pytest.fixture
def _rule_strings():
    rule_strings = {
        'Rule1_pd': "((X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna()))&(X['D'].isin(['foo', 'bar']))&(X['E']==X['F'])&(X['G'].fillna('')=='')",
        'Rule1_np': "((X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan))))&(X['D'].isin(['foo', 'bar']))&(X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan))&(X['G'].fillna('')=='')",
        'Rule2': "(X['A'].str.startswith(')('))",
        'Rule3_single_cond_brackets': "(X['A']>10)",
        'Rule3_single_cond_no_brackets': "X['A']>10",
    }
    return rule_strings


@pytest.fixture
def _rule_dicts():
    rule_dict_Rule1 = {'condition': 'AND',
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
    rule_dict_Rule2 = {'condition': 'AND',
                       'rules': [
                           {'field': 'A', 'operator': 'begins_with',
                               'value': ')('}
                       ]
                       }
    rule_dict_Rule3 = {'condition': 'AND',
                       'rules': [
                           {'field': 'A', 'operator': 'greater',
                               'value': 10.0}
                       ]
                       }
    rule_dict = {
        'Rule1_pd': rule_dict_Rule1,
        'Rule1_np': rule_dict_Rule1,
        'Rule2': rule_dict_Rule2,
        'Rule3_single_cond_brackets': rule_dict_Rule3,
        'Rule3_single_cond_no_brackets': rule_dict_Rule3,
    }
    return rule_dict


@pytest.fixture
def _single_condition_str_list():
    single_condition_str_list = ["X['A']>=60.0",
                                 "X['B'].str.startswith('foo', na=False)",
                                 "X['C'].isna()",
                                 "X['D'].isin(['foo', 'bar'])",
                                 "X['E']==X['F']",
                                 "X['G'].fillna('')==''"]
    return single_condition_str_list


@pytest.fixture
def _single_condition_dict_list():
    single_condition_dict_list = [{'field': 'A',
                                   'operator': 'greater_or_equal',
                                   'value': 60.0},
                                  {'field': 'B',
                                   'operator': 'begins_with',
                                   'value': 'foo'},
                                  {'field': 'C',
                                   'operator': 'is_null',
                                   'value': None},
                                  {'field': 'D',
                                   'operator': 'in',
                                   'value': ['foo', 'bar']},
                                  {'field': 'E',
                                   'operator': 'equal_field',
                                   'value': 'F'},
                                  {'field': 'G',
                                   'operator': 'is_empty',
                                   'value': None}]
    return single_condition_dict_list


@pytest.fixture
def _expected_top_level_parentheses_idxs():
    expected_results = {
        'Rule1_pd': {1: 72, 75: 102, 105: 119, 122: 143},
        'Rule1_np': {1: 126, 129: 156, 159: 225, 228: 249},
        'Rule2': {1: 28},
        'Rule3_single_cond_brackets': {1: 10},
        'Rule3_single_cond_no_brackets': {},
    }
    return expected_results


@pytest.fixture
def _expected_conditions_string_lists():
    expected_results = {
        'Rule1_pd': ["(X['A']>=60.0)|(X['B'].str.startswith('foo', na=False))|(X['C'].isna())",
                     "X['D'].isin(['foo', 'bar'])",
                     "X['E']==X['F']",
                     "X['G'].fillna('')==''"],
        'Rule1_np': ["(X['A'].to_numpy(na_value=np.nan)>=60.0)|(X['B'].str.startswith('foo', na=False))|(pd.isna(X['C'].to_numpy(na_value=np.nan)))",
                     "X['D'].isin(['foo', 'bar'])",
                     "X['E'].to_numpy(na_value=np.nan)==X['F'].to_numpy(na_value=np.nan)",
                     "X['G'].fillna('')==''"],
        'Rule2': ["X['A'].str.startswith(')(')"],
        'Rule3_single_cond_brackets': ["X['A']>10"],
        'Rule3_single_cond_no_brackets': [],
    }
    return expected_results


@pytest.fixture
def _expected_connecting_cond_lists():
    expected_results = {
        'Rule1_pd': ['&', '&', '&'],
        'Rule1_np': ['&', '&', '&'],
        'Rule2': [],
        'Rule3_single_cond_brackets': [],
        'Rule3_single_cond_no_brackets': []
    }
    return expected_results


def test_convert(_rule_strings, _rule_dicts):
    rule_strings = _rule_strings
    expected_rule_dicts = _rule_dicts
    r = _ConvertRuleStringsToRuleDicts(rule_strings=rule_strings)
    rule_dicts = r.convert()
    assert rule_dicts == expected_rule_dicts


def test_convert_rule(_rule_strings, _rule_dicts):
    rule_strings = _rule_strings
    expected_rule_dicts = _rule_dicts
    for rule_name, rule_string in rule_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        rule_dict = r._convert_rule(rule_string=rule_string)
        assert rule_dict == expected_rule_dicts[rule_name]


def test_recurse_convert_rule_string_conditions(_rule_strings, _rule_dicts):
    rule_strings = _rule_strings
    expected_rule_dicts = _rule_dicts
    # Add rule with addition enclosing brackets to test they are removed
    rule_strings_ = rule_strings.copy()
    rule_w_bracketted = f"({rule_strings_['Rule1_pd']})"
    rule_strings_['Rule1_pd_bracketted'] = rule_w_bracketted
    expected_rule_dicts_ = expected_rule_dicts.copy()
    expected_rule_dicts_[
        'Rule1_pd_bracketted'] = expected_rule_dicts['Rule1_pd']
    for rule_name, rule_string in rule_strings_.items():
        # This function only for rules with > 1 condition
        if rule_name in ['Rule2', 'Rule3_single_cond_brackets', 'Rule3_single_cond_no_brackets']:
            continue
        parent_dict = {
            'condition': None,
            'rules': []
        }
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        rule_dict = r._recurse_convert_rule_string_conditions(
            rule_string=rule_string, parent_dict=parent_dict
        )
        assert rule_dict == expected_rule_dicts_[rule_name]


def test_convert_rule_string_conditions(_expected_conditions_string_lists, _rule_dicts):
    expected_rule_dicts = _rule_dicts
    conditions_string_lists = _expected_conditions_string_lists
    for rule_name, conditions_string_list in conditions_string_lists.items():
        # Function doesn't work with conditions_string_list for Rule3_single_cond_no_brackets
        # since _return_conditions_string_list returns empty list for that rule
        if rule_name == 'Rule3_single_cond_no_brackets':
            continue
        parent_dict = {
            'condition': None,
            'rules': []
        }
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        rule_dict = r._convert_rule_string_conditions(conditions_string_list=conditions_string_list,
                                                      parent_dict=parent_dict)
        rule_dict['condition'] = 'AND'
        assert rule_dict == expected_rule_dicts[rule_name]


def test_create_condition_dict(_single_condition_str_list,
                               _single_condition_dict_list):
    single_condition_str_list = _single_condition_str_list
    single_condition_dict_list = _single_condition_dict_list
    for i, single_condition in enumerate(single_condition_str_list):
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        single_dict = r._create_condition_dict(rule_string=single_condition)
        assert single_dict == single_condition_dict_list[i]


def test_extract_components_from_condition_string(_single_condition_str_list,
                                                  _single_condition_dict_list):
    single_condition_str_list = _single_condition_str_list
    single_condition_dict_list = _single_condition_dict_list
    for i, single_condition in enumerate(single_condition_str_list):
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        feature, operator, value = r._extract_components_from_condition_string(
            condition_string=single_condition)
        assert feature == single_condition_dict_list[i]['field']
        assert operator == single_condition_dict_list[i]['operator']
        assert value == single_condition_dict_list[i]['value']


def test_find_top_level_parentheses_idx(_rule_strings, _expected_top_level_parentheses_idxs):
    rule_strings = _rule_strings
    expected_results = _expected_top_level_parentheses_idxs
    for rule_name, rule_string in rule_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        top_level_idx = r._find_top_level_parentheses_idx(
            rule_string=rule_string)
        assert top_level_idx == expected_results[rule_name]


def test_return_conditions_string_list(_rule_strings, _expected_top_level_parentheses_idxs,
                                       _expected_conditions_string_lists):
    rule_strings = _rule_strings
    top_level_parentheses_idxs = _expected_top_level_parentheses_idxs
    expected_results = _expected_conditions_string_lists
    for rule_name, rule_string in rule_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        conditions_string_list = r._return_conditions_string_list(
            parentheses_pair_idxs=top_level_parentheses_idxs[rule_name],
            rule_string=rule_string)
        assert conditions_string_list == expected_results[rule_name]


def test_find_connecting_conditions(_rule_strings, _expected_top_level_parentheses_idxs,
                                    _expected_connecting_cond_lists):
    rule_strings = _rule_strings
    top_level_parentheses_idxs = _expected_top_level_parentheses_idxs
    expected_results = _expected_connecting_cond_lists
    for rule_name, rule_string in rule_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        connecting_cond_list = r._find_connecting_conditions(parentheses_pair_idxs=top_level_parentheses_idxs[rule_name],
                                                             rule_string=rule_string)
        assert connecting_cond_list == expected_results[rule_name]


def test_return_connecting_condition(_expected_connecting_cond_lists):
    connecting_cond_lists = _expected_connecting_cond_lists
    condition_lookup = {
        '|': 'OR',
        '&': 'AND'
    }
    for rule_name, connecting_cond_list in connecting_cond_lists.items():
        try:
            r = _ConvertRuleStringsToRuleDicts(rule_strings={})
            connecting_dict_condition = r._return_connecting_condition(connecting_cond_list=connecting_cond_list,
                                                                       condition_lookup=condition_lookup)
            assert connecting_dict_condition == 'AND'
            assert 'Rule1' in rule_name
        except Exception as e:
            assert str(
                e) == 'More than one connecting condition for a given level'
            assert rule_name in [
                'Rule2', 'Rule3_single_cond_brackets', 'Rule3_single_cond_no_brackets']


def test_create_rule_condition_dict():
    args = ('A', 'greater_than', 0)
    expected_result = {
        'field': 'A',
        'operator': 'greater_than',
        'value': 0
    }
    r = _ConvertRuleStringsToRuleDicts(rule_strings={})
    condition_dict = r._create_rule_condition_dict(*args)
    assert condition_dict == expected_result


def test_return_value_for_pandas_str_based_operators():
    condition_strings = {
        '].str.startswith': "X['B'].str.startswith('foo', na=False)",
        '].str.endswith': "X['B'].str.endswith('foo', na=False)",
        '].str.contains': "X['B'].str.contains('foo', na=False)"
    }
    for operator, condition_string in condition_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        value = r._return_value_for_pandas_str_based_operators(
            condition_string=condition_string, operator=operator)
        assert value == 'foo'


def test_return_value_for_pandas_is_in_operator():
    condition_strings = {
        '].isin': "X['B'].isin(['foo', 'bar'])",
    }
    for operator, condition_string in condition_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        value = r._return_value_for_pandas_is_in_operator(
            condition_string=condition_string, operator=operator)
        assert value == ['foo', 'bar']


def test_return_value_for_standard_operators():
    condition_strings = {
        '>=': "X['B']>=1",
        "fillna('')!=": "X['B'].fillna('')!=''",
        '==': "X['B']=='foo'",
    }
    expected_results = {
        '>=': 1,
        "fillna('')!=": None,
        '==': "foo"
    }
    for operator, condition_string in condition_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        value = r._return_value_for_standard_operators(
            condition_string=condition_string, operator=operator)
        assert value == expected_results[operator]


def test_return_value_for_field_level_comparison():
    condition_strings = {
        "==X['": "X['B']==X['C']",
    }
    for operator, condition_string in condition_strings.items():
        r = _ConvertRuleStringsToRuleDicts(rule_strings={})
        value = r._return_value_for_field_level_comparison(
            condition_string=condition_string, operator=operator)
        assert value == 'C'


def test_errors():
    r = _ConvertRuleStringsToRuleDicts(rule_strings={})
    with pytest.raises(Exception, match='Operator not currently supported in Iguanas. Rule cannot be parsed.'):
        r._extract_components_from_condition_string("X['A'].not('james')")
