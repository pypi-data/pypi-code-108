import databricks.koalas as ks
import numpy as np
import iguanas.metrics as iguanas_metrics
import pytest


@pytest.fixture
def create_data():
    np.random.seed(0)
    y_pred = np.random.randint(0, 2, 1000)
    y_true = np.random.randint(0, 2, 1000)
    y_preds = np.random.randint(0, 2, (1000, 2))
    weights = y_true * 10
    y_true_ks, y_pred_ks, y_preds_ks, weights_ks = ks.Series(y_true, name='label_'), ks.Series(
        y_pred, name='A'), ks.DataFrame(y_preds, columns=['A', 'B']), ks.Series(weights, name='sample_weight_')
    return y_true_ks, y_pred_ks, weights_ks, y_true, y_pred, weights, y_preds_ks, y_preds


def test_AlertsPerDay(create_data):
    np.random.seed(0)
    _, y_pred_ks, _, _, _, _, y_preds_ks, _ = create_data
    apd = iguanas_metrics.AlertsPerDay(
        n_alerts_expected_per_day=50, no_of_days_in_file=30)
    apd_calc = apd.fit(y_pred_ks)
    apd_exp = -1102.2400000000002
    assert apd_calc == apd_exp
    apd_calc = apd.fit(y_preds_ks)
    apd_exp = np.array([-1073.65444444, -1102.24])
    np.testing.assert_array_almost_equal(apd_calc, apd_exp)


def test_PercVolume(create_data):
    np.random.seed(0)
    _, y_pred_ks, _, _, _, _, y_preds_ks, _ = create_data
    pv = iguanas_metrics.PercVolume(perc_vol_expected=0.02)
    pv_calc = pv.fit(y_pred_ks)
    pv_exp = -0.234256
    assert pv_calc == pv_exp
    pv_calc = pv.fit(y_preds_ks)
    pv_exp = np.array([-0.247009, -0.234256])
    np.testing.assert_array_almost_equal(pv_calc, pv_exp)
