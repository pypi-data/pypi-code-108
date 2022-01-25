import pandas as pd

from bamboolib.df_manager import DfManager


def test_reset_index():
    # explicitly set index
    df = pd.DataFrame(dict(a=[1, 2], b=[2, 3])).set_index("a")
    assert DfManager(df, symbols=locals())._did_reset_index

    # unnamed index from series/list
    df = pd.DataFrame(dict(a=[1, 2], b=[2, 3]), index=["a", "b"])
    assert DfManager(df, symbols=locals())._did_reset_index

    # no further normalization after we once normalized
    df = pd.DataFrame(dict(a=[1, 2], b=[2, 3]), index=["a", "b"])
    normalized_df = DfManager(df, symbols=locals()).get_current_df()
    assert not DfManager(normalized_df, symbols=locals())._df_was_normalized()
