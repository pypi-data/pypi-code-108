import numpy as np
import pandas as pd
import iguanas.metrics as iguanas_metrics
import pytest


@pytest.fixture
def create_data():
    np.random.seed(0)
    y_pred = np.random.randint(0, 2, 1000)
    y_true = np.random.randint(0, 2, 1000)
    y_preds = pd.DataFrame(np.random.randint(0, 2, size=(1000, 2)))
    weights = y_true * 10
    return y_true, y_pred, weights, y_preds


def test_AlertsPerDay(create_data):
    np.random.seed(0)
    _, y_pred, _, y_preds = create_data
    apd = iguanas_metrics.AlertsPerDay(
        n_alerts_expected_per_day=50, no_of_days_in_file=30)
    apd_calc = apd.fit(y_pred)
    apd_exp = -1102.2400000000002
    assert apd_calc == apd_exp
    apd_calc = apd.fit(y_preds)
    apd_exp = np.array([-1073.65444444, -1102.24])
    np.testing.assert_array_almost_equal(apd_calc, apd_exp)


def test_PercVolume(create_data):
    np.random.seed(0)
    _, y_pred, _, y_preds = create_data
    pv = iguanas_metrics.PercVolume(perc_vol_expected=0.02)
    pv_calc = pv.fit(y_pred)
    pv_exp = -0.234256
    assert pv_calc == pv_exp
    pv_calc = pv.fit(y_preds)
    pv_exp = np.array([-0.247009, -0.234256])
    np.testing.assert_array_almost_equal(pv_calc, pv_exp)


def test_repr():
    apd = iguanas_metrics.AlertsPerDay(
        n_alerts_expected_per_day=10, no_of_days_in_file=5)
    pv = iguanas_metrics.PercVolume(perc_vol_expected=0.1)
    assert 'AlertsPerDay with n_alerts_expected_per_day=10, no_of_days_in_file=5' == apd.__repr__()
    assert 'PercVolume with perc_vol_expected=0.1' == pv.__repr__()


def test_warnings_AlertsPerDay():
    apd = iguanas_metrics.AlertsPerDay(
        n_alerts_expected_per_day=1, no_of_days_in_file=1)
    with pytest.raises(TypeError, match="`y_preds` must be a numpy.ndarray or pandas.core.series.Series or pandas.core.frame.DataFrame or databricks.koalas.series.Series or databricks.koalas.frame.DataFrame. Current type is list."):
        apd.fit([])


def test_warnings_PercVolume():
    pv = iguanas_metrics.PercVolume(perc_vol_expected=0.2)
    with pytest.raises(TypeError, match="`y_preds` must be a numpy.ndarray or pandas.core.series.Series or pandas.core.frame.DataFrame or databricks.koalas.series.Series or databricks.koalas.frame.DataFrame. Current type is list."):
        pv.fit([])
