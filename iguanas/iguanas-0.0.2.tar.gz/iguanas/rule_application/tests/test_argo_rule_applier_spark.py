import databricks.koalas as ks
import pandas as pd
import numpy as np
import random
import pytest
from iguanas.rule_application import RuleApplier


@pytest.fixture
def create_data():
    random.seed(0)
    np.random.seed(0)
    X = ks.DataFrame(data={
        "num_distinct_txn_per_email_1day": np.random.randint(0, 10, 1000),
        "num_distinct_txn_per_email_7day": np.random.randint(0, 70, 1000),
        "ip_country_us": np.random.uniform(0, 1, 1000) > 0.8,
        "email_alpharatio":  np.random.uniform(0, 1, 1000),
        "email_kb_distance": np.random.uniform(0, 1, 1000),
    },
        index=list(range(0, 1000))
    )
    X = X.astype(float)
    return X


@pytest.fixture
def return_dummy_rules():
    rules = {
        'Rule1': "X['num_distinct_txn_per_email_7day']>=7",
        'Rule2': "X['email_alpharatio']<=0.5",
        'Rule3': "X['num_distinct_txn_per_email_1day']>=1",
        'Rule4': "X['email_kb_distance']<=0.5",
        'Rule5': "X['ip_country_us']==False",
        'Rule6': "X['num_distinct_txn_per_email_1day']<=3",
        'Rule7': "X['num_distinct_txn_per_email_7day']<=5",
        'Rule8': "X['email_kb_distance']>=0.61",
        'Rule9': "X['email_alpharatio']>=0.5"
    }
    return rules


@pytest.fixture
def return_exp_results():
    X_rules_sums = pd.Series({
        'Rule1': 900,
        'Rule2': 525,
        'Rule3': 901,
        'Rule4': 522,
        'Rule5': 791,
        'Rule6': 414,
        'Rule7': 85,
        'Rule8': 354,
        'Rule9': 475
    })
    return X_rules_sums


@ pytest.fixture
def ara_instantiated(return_dummy_rules):
    rules = return_dummy_rules
    ara = RuleApplier(rules)
    return ara


def test_transform(create_data, ara_instantiated, return_exp_results):
    X = create_data
    exp_X_rules_sums = return_exp_results
    ara = ara_instantiated
    X_rules = ara.transform(X)
    assert all(
        X_rules.sum().sort_index().to_pandas() == exp_X_rules_sums.sort_index()
    )
    assert X_rules.shape == (1000, 9)
    assert X_rules.sum().sum() == 4967


def test_get_X_rules(create_data, ara_instantiated):
    X = create_data
    ara = ara_instantiated
    X_rules = ara._get_X_rules(X)
    assert X_rules.shape == (1000, 9)
    assert X_rules.sum().sum() == 4967


def test_missing_feat_error(create_data):
    X = create_data
    rule_strings = {'Rule1': "(X['Z']>1)"}
    ara = RuleApplier(rule_strings=rule_strings)
    with pytest.raises(KeyError, match="Feature 'Z' in rule `Rule1` not found in `X`") as e:
        ara.transform(X)


def test_type_errors(create_data):
    X = create_data
    ara = RuleApplier(
        rule_strings={'Rule1': "(X['num_distinct_txn_per_email_7day']>1)"})
    with pytest.raises(TypeError, match="`X` must be a pandas.core.frame.DataFrame or databricks.koalas.frame.DataFrame. Current type is list.") as e:
        ara.transform(X=[])
