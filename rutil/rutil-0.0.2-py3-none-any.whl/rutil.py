import pandas as pd


def pystr(
    df: pd.DataFrame,
    colname_len: int = 18,
    dtype_len: int = 12,
    content_len: int = 75,
) -> pd.DataFrame:

    print(f"Pandas DataFrame {df.shape[0]} obs. of {df.shape[1]} variables")
    n_values = 50 if df.shape[0] > 50 else df.shape[0]

    if len(df) == 0:
        return df

    for col_name in df.columns:

        str_dtype = _parse_dtypes(df, col_name, dtype_len)

        if "float" in str_dtype:
            rounded_vals_str = [round(x, 1) if x > 1 else round(x, 2) for x in df[col_name].values[:n_values]]
            values_str = ", ".join([str(x) for x in [rounded_vals_str]])
        if "str" in str_dtype:
            values_str = ", ".join([f"\042{x}\042" for x in df[col_name].values[:n_values]])
        else:
            values_str = ", ".join([str(x) for x in df[col_name].values[:n_values]])

        if len(values_str) > content_len:
            values_str = f"{values_str[:content_len]}..."

        print(f"$ {_parse_string(col_name,colname_len)}: {str_dtype} {values_str}")

    return df


def _parse_string(string_name: str, colname_len: int = 28) -> str:

    if len(string_name) > colname_len:
        return f"{string_name[:colname_len-2]}.."

    if len(string_name) < colname_len:
        return string_name.ljust(colname_len)

    return string_name


def _contains(string: str, string_list: list) -> bool:

    return any([x in string for x in string_list])


def _parse_dtypes(df: pd.DataFrame, col_name: str, dtype_len: int) -> str:

    SAMPLE_SIZE = 30
    PRIMITIVE_TYPES = ["int", "float", "bool"]

    if len(df) < SAMPLE_SIZE:
        SAMPLE_SIZE = len(df)

    data_type = str(df.dtypes[col_name])

    if _contains(data_type, PRIMITIVE_TYPES):
        return _parse_string(data_type, dtype_len)

    classes = list(dict.fromkeys([str(type(x)) for x in df[col_name].sample(SAMPLE_SIZE).dropna()]))

    if len(classes) == 0:
        return _parse_string("Null", dtype_len)
    if len(classes) == 1:
        return _parse_string(classes[0].replace("<class '", "").replace("'>", ""), dtype_len)

    return _parse_string(f"{len(classes)} types", dtype_len)
