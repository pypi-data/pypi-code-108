from qpd_test import assert_df_eq
import pandas as pd
from pytest import raises


def test_assert_df_eq():
    a = pd.DataFrame([[0, 1]], columns=["a", "b"])
    assert_df_eq(a, a)
    assert_df_eq(a, [[0.0, 1.0]], ["a", "b"])
    assert not assert_df_eq(a, [[0.001, 1.001]], ["a", "b"], throw=False)
    assert_df_eq(a, [[0.001, 1.001]], ["a", "b"], digits=1)
    assert_df_eq(a, [[1, 0]], ["b", "a"])
    assert not assert_df_eq(a, [[1, 0]], ["b", "a"], check_col_order=True, throw=False)
    assert not assert_df_eq(a, [[10, 0]], ["b", "a"], throw=False)
    assert_df_eq(a, [[10, 0]], ["b", "a"], check_content=False)
    with raises(AssertionError):
        assert_df_eq(a, [[1.0, 1.0]], ["a", "b"])

    a = pd.DataFrame([[0, 1], [3, 4]], columns=["a", "b"])
    b = pd.DataFrame([[3, 4], [0, 1]], columns=["a", "b"])
    assert_df_eq(a, b)
    assert not assert_df_eq(a, b, check_order=True, throw=False)
