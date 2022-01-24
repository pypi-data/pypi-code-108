from typing import Any

import pandas  # type: ignore


def pandas_to_python_type(series: pandas.Series):
    if pandas.api.types.is_bool_dtype(series):
        return type(True)
    elif pandas.api.types.is_float_dtype(series):
        return type(1.0)
    elif pandas.api.types.is_integer_dtype(series):
        return type(1)
    elif pandas.api.types.is_string_dtype(series):
        if pandas.api.types.is_object_dtype(series):
            return Any
        else:
            return type("a")
    else:
        return None
