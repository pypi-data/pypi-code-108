import pytest
import pandas as pd
import iguanas.rule_scoring.rule_score_scalers as rss


@pytest.fixture
def create_data():
    pos_rule_scores = pd.Series({'A': 2, 'B': 3, 'C': 10, 'D': 5, 'E': 12})
    neg_rule_scores = -pos_rule_scores
    return [pos_rule_scores, neg_rule_scores]


@pytest.fixture
def expected_results_ConstantScaler():
    pos_rule_scores_scaled = pd.Series(
        {'A': 17, 'B': 25, 'C': 83, 'D': 42, 'E': 100})
    neg_rule_scores_scaled = -pos_rule_scores_scaled
    return pos_rule_scores_scaled, neg_rule_scores_scaled


@pytest.fixture
def expected_results_MinMaxScaler():
    pos_rule_scores_scaled = pd.Series(
        {'A': 10, 'B': 19, 'C': 82, 'D': 37, 'E': 100})
    neg_rule_scores_scaled = -pos_rule_scores_scaled
    return pos_rule_scores_scaled, neg_rule_scores_scaled


def test_ConstantScaler(create_data, expected_results_ConstantScaler):
    def _calc_result(limit, scores):
        if limit == -100:
            return round((limit / scores.min()) * scores).astype(int)
        if limit == 100:
            return round((limit / scores.max()) * scores).astype(int)
    input_scores = create_data
    expected_results = expected_results_ConstantScaler
    limits = [100, -100]
    for i, scores in enumerate(input_scores):
        cs = rss.ConstantScaler(limit=limits[i])
        result = cs.fit(scores)
        assert all(result == expected_results[i])
        calc_result = _calc_result(limits[i], scores)
        assert all(result == calc_result)


def test_MinMaxScaler(create_data, expected_results_MinMaxScaler):
    input_scores = create_data
    expected_results = expected_results_MinMaxScaler
    min_max_values = [(10, 100), (-100, -10)]
    for i, scores in enumerate(input_scores):
        mms = rss.MinMaxScaler(
            min_value=min_max_values[i][0], max_value=min_max_values[i][1])
        result = mms.fit(scores)
        assert all(result == expected_results[i])
        assert result.min() == min_max_values[i][0]
        assert result.max() == min_max_values[i][1]


def test_errors():
    mms = rss.MinMaxScaler(0, 100)
    cs = rss.ConstantScaler(100)
    with pytest.raises(ValueError, match='rule_scores must contain only negative scores or only positive scores, not a mixture'):
        mms.fit(pd.Series([-10, 10, 0, 10]))
    with pytest.raises(ValueError, match='rule_scores must contain only negative scores or only positive scores, not a mixture'):
        cs.fit(pd.Series([-10, 10, 0, 10]))
