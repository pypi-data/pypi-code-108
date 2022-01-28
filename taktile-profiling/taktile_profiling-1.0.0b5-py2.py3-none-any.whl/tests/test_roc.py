import numpy as np
import pytest

from profiling.accuracy import binary_tpr_fpr


@pytest.mark.parametrize(
    "y, preds, tpr_expected, fpr_expected",
    [
        ([0, 0], [0, 0], [0, 0], [0, 1]),
        ([0, 0], [0, 1], [0, 0, 0], [0, 0.5, 1]),
        ([0, 1], [0, 0], [0, 1], [0, 1]),
        ([0, 1], [0, 1], [0, 1, 1], [0, 0, 1]),
        ([1, 1], [0, 1], [0, 0.5, 1], [0, 0, 0]),
    ],
)
def test_binary_tpr_fpr(y, preds, tpr_expected, fpr_expected):
    y = np.array(y)
    preds = np.array(preds)
    tpr, fpr = binary_tpr_fpr(y, preds)

    assert np.array_equal(tpr, tpr_expected)
    assert np.array_equal(fpr, fpr_expected)
