from datetime import date, datetime

import pandas as pd
import pytest

from profiling.utils import df_to_dict

dict_simple = {"Integer": [0], "Float": [0.0], "String": ["a"]}
df_simple = pd.DataFrame.from_dict(dict_simple)

dict_complex = {
    "Integer": [1, 2, 3],
    "Float": [None, 2.0, 3.0],
    "String": [None, "", "c"],
    "Categorical": ["a", "b", "c"],
    "Date Variable": [date(2020, 1, 1), date(2020, 1, 1), date(1, 1, 1)],
    "Datetime Variable": [
        datetime(2020, 1, 1),
        datetime(2020, 1, 1),
        datetime(1, 1, 1),
    ],
}

df_complex = pd.DataFrame.from_dict(dict_complex)
df_complex["Categorical"] = df_complex["Categorical"].astype("category")


@pytest.mark.parametrize(
    "input_df,expected_output", [(df_simple, dict_simple), (df_complex, dict_complex)]
)
def test_dict_conversion(input_df, expected_output):
    output = df_to_dict(input_df)
    assert output == expected_output
