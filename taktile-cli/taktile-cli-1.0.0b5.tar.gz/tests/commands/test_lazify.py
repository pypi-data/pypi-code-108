import pathlib
import tempfile

import pandas as pd  # type: ignore
import pytest

from tktl.commands.lazify import lazify_file
from tktl.future.lazy_loading import load_background_data_from_lazified_pq


@pytest.mark.parametrize(
    "df, background_data",
    [
        (
            pd.DataFrame.from_dict(
                {
                    "Integer": pd.Series([1], dtype="int64"),
                    "Float": pd.Series([3.0], dtype="float64"),
                    "Object": pd.Series(["c"], dtype="object"),
                    "Bool": pd.Series([True], dtype="bool"),
                    "Categorical": pd.Series(["a"], dtype="category"),
                    "Datetime": pd.Series(["2020-01-01"], dtype="datetime64[ns]"),
                }
            ),
            pd.DataFrame.from_dict(
                {
                    "Integer": pd.Series([1], dtype="int64"),
                    "Float": pd.Series([3.0], dtype="float64"),
                    "Object": pd.Series(["c"], dtype="object"),
                    "Bool": pd.Series([True], dtype="bool"),
                    "Categorical": pd.Series(["a"], dtype="category"),
                    "Datetime": pd.Series(["2020-01-01"], dtype="datetime64[ns]"),
                }
            ),
        ),
        (
            pd.DataFrame.from_dict(
                {
                    "Integer": pd.Series([1, 3, 5], dtype="int64"),
                    "Float": pd.Series([3.0, 3.5, 4.0], dtype="float64"),
                    "Object": pd.Series(["c", "d", "c"], dtype="object"),
                    "Bool": pd.Series([True, False, False], dtype="bool"),
                    "Categorical": pd.Series(["a", "a", "a"], dtype="category"),
                    "Datetime": pd.Series(
                        ["2020-01-01", "2020-01-01", "2020-01-01"],
                        dtype="datetime64[ns]",
                    ),
                }
            ),
            pd.DataFrame.from_dict(
                {
                    "Integer": pd.Series([3], dtype="int64"),
                    "Float": pd.Series([3.5], dtype="float64"),
                    "Object": pd.Series(["c"], dtype="object"),
                    "Bool": pd.Series([False], dtype="bool"),
                    "Categorical": pd.Series(["a"], dtype="category"),
                    "Datetime": pd.Series(["2020-01-01"], dtype="datetime64[ns]"),
                }
            ),
        ),
    ],
)
def test_file_lazification(df, background_data):

    with tempfile.TemporaryDirectory() as tmp_dir:
        path = pathlib.Path(tmp_dir) / "test.pqt"

        df.to_parquet(path)
        lazify_file(source_path=path, target_path=path, data=None)

        df_loaded = load_background_data_from_lazified_pq(path)

    pd.testing.assert_frame_equal(df_loaded, background_data)
