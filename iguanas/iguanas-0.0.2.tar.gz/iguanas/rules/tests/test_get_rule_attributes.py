import pytest
from iguanas.rules._get_rule_attributes import _GetRuleFeatures


@pytest.fixture
def _rule_dict():
    rule_dicts = {
        'BulkLowCostPerPayPalID': {'condition': 'AND',
                                   'rules': [{'condition': 'OR',
                                              'rules': [{'field': 'payer_id_sum_approved_txn_amt_per_paypalid_1day',
                                                         'operator': 'greater_or_equal',
                                                         'value': 60.0},
                                                        {'field': 'payer_id_sum_approved_txn_amt_per_paypalid_7day',
                                                         'operator': 'greater_or_equal',
                                                         'value': 120.0},
                                                        {'field': 'payer_id_sum_approved_txn_amt_per_paypalid_30day',
                                                         'operator': 'greater_or_equal',
                                                         'value': 500.0}]},
                                             {'field': 'num_items',
                                              'operator': 'equal', 'value': 1.0},
                                             {'field': 'total_num_items_ordered',
                                              'operator': 'greater_or_equal',
                                              'value': 2.0}]},
        'BeyondMLScore': {'condition': 'OR',
                          'rules': [{'condition': 'AND',
                                     'rules': [{'field': 'ml_cc_v0', 'operator': 'greater', 'value': 0.315},
                                               {'condition': 'OR',
                                                'rules': [{'field': 'method_clean',
                                                           'operator': 'equal',
                                                           'value': 'checkout'},
                                                          {'field': 'method_clean',
                                                           'operator': 'equal',
                                                           'value': 'checkout_cards'},
                                                          {'field': 'method_clean', 'operator': 'equal',
                                                           'value': 'checkout_apm'},
                                                          {'field': 'method_clean',
                                                           'operator': 'equal',
                                                           'value': 'checkout_apple_pay'},
                                                          {'field': 'method_clean',
                                                           'operator': 'equal',
                                                           'value': 'checkoutcomcards'},
                                                          {'field': 'method_clean',
                                                           'operator': 'equal',
                                                           'value': 'checkoutcom_card_payment'}]}]},
                                    {'condition': 'AND',
                                     'rules': [{'field': 'ml_pp_v0', 'operator': 'greater', 'value': 0.396},
                                               {'condition': 'OR',
                                                'rules': [{'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkout'},
                                                          {'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkout_cards'},
                                                          {'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkout_apm'},
                                                          {'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkout_apple_pay'},
                                                          {'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkoutcomcards'},
                                                          {'field': 'method_clean',
                                                           'operator': 'not_equal',
                                                           'value': 'checkoutcom_card_payment'}]}]}]},
        'SingleLevel': {'condition': 'AND',
                        'rules': [
                            {'field': 'ml_pp_v0',
                                'operator': 'greater', 'value': 0.396},
                            {'field': 'ml_pp_v1',
                                'operator': 'greater', 'value': 0.396},
                            {'field': 'ml_pp_v2', 'operator': 'greater', 'value': 0.396}
                        ]
                        },
        'FieldComparison': {'condition': 'AND',
                            'rules': [
                                {'field': 'shipping_address',
                                 'operator': 'equal_field',
                                 'value': 'billing_address'},
                                {'field': 'ml_pp_v0',
                                 'operator': 'greater_field',
                                 'value': 'ml_pp_v1'}
                            ]
                            }
    }
    return rule_dicts


def test_get(_rule_dict):
    exp_result = {
        'BulkLowCostPerPayPalID': {'num_items',
                                   'payer_id_sum_approved_txn_amt_per_paypalid_1day',
                                   'payer_id_sum_approved_txn_amt_per_paypalid_30day',
                                   'payer_id_sum_approved_txn_amt_per_paypalid_7day',
                                   'total_num_items_ordered'},
        'BeyondMLScore': {'method_clean', 'ml_cc_v0', 'ml_pp_v0'},
        'SingleLevel': {'ml_pp_v0', 'ml_pp_v1', 'ml_pp_v2'},
        'FieldComparison': {'shipping_address', 'billing_address', 'ml_pp_v0', 'ml_pp_v1'}
    }
    rule_dicts = _rule_dict
    grf = _GetRuleFeatures(rule_dicts=rule_dicts)
    assert grf.get() == exp_result


def test_get_rule_features(_rule_dict):
    exp_result = {'num_items',
                  'payer_id_sum_approved_txn_amt_per_paypalid_1day',
                  'payer_id_sum_approved_txn_amt_per_paypalid_30day',
                  'payer_id_sum_approved_txn_amt_per_paypalid_7day',
                  'total_num_items_ordered'}
    rule_dicts = _rule_dict
    grf = _GetRuleFeatures(rule_dicts=rule_dicts)
    assert grf._get_rule_features(
        rule_dict=rule_dicts['BulkLowCostPerPayPalID']) == exp_result


def test_recurse_add_rule_features(_rule_dict):
    exp_result = {'num_items',
                  'payer_id_sum_approved_txn_amt_per_paypalid_1day',
                  'payer_id_sum_approved_txn_amt_per_paypalid_30day',
                  'payer_id_sum_approved_txn_amt_per_paypalid_7day',
                  'total_num_items_ordered'}
    rule_dicts = _rule_dict
    grf = _GetRuleFeatures(rule_dicts=rule_dicts)
    assert grf._recurse_add_rule_features(
        rules_list=rule_dicts['BulkLowCostPerPayPalID']['rules'], feature_set=set()) == exp_result
