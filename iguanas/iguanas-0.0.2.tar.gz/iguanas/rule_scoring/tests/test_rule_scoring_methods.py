import pytest
import numpy as np
import pandas as pd
import iguanas.rule_scoring.rule_scoring_methods as rsm
from sklearn.metrics import precision_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import math
from iguanas.metrics.classification import Precision


@pytest.fixture
def create_data():
    np.random.seed(0)
    X_rules = pd.DataFrame({
        'A': np.random.randint(0, 2, 100),
        'B': np.random.randint(0, 2, 100),
        'C': np.random.randint(0, 2, 100),
    })
    y = pd.Series(np.random.randint(0, 2, 100))
    weights = y * 10
    return X_rules, y, weights


def test_PerformanceScorer(create_data):
    X_rules, y, weights = create_data
    ws = rsm.PerformanceScorer(Precision().fit)
    for w in [None, weights]:
        rule_scores = ws.fit(X_rules, y, w)
        precisions = X_rules.apply(lambda x: precision_score(
            y_true=y, y_pred=x, sample_weight=w))
        assert all(rule_scores == precisions)


def test_LogRegScorer(create_data):
    X_rules, y, weights = create_data
    lr = rsm.LogRegScorer()
    for w in [None, weights]:
        rule_scores = lr.fit(X_rules, y, w)
        lr_sk = LogisticRegression()
        lr_sk.fit(X_rules, y, w)
        scores = np.array(
            list(map(lambda x: math.exp(x), lr_sk.coef_[0])))
        exp_rule_scores = pd.Series(scores, X_rules.columns)
        assert all(rule_scores == exp_rule_scores)


def test_RandomForestScorer(create_data):
    X_rules, y, weights = create_data
    rf = rsm.RandomForestScorer()
    for w in [None, weights]:
        rule_scores = rf.fit(X_rules, y, w)
        rf_sk = RandomForestClassifier(random_state=0)
        rf_sk.fit(X_rules, y, w)
        scores = rf_sk.feature_importances_
        exp_rule_scores = pd.Series(scores, X_rules.columns)
        assert all(rule_scores == exp_rule_scores)
