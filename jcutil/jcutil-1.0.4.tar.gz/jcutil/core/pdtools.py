# pandas tools
from jcramda import compose, attr, curry, partial, flat_concat, is_a


try:
    import pandas as pd
    import numpy as np
    col_value = curry(lambda col, df: compose(lambda s: s.iloc[0], attr(col))(df))

    df_dt = partial(pd.to_datetime, errors='ignore')

    df_to_json = curry(lambda df: df.to_json(
        orient='records',
        default_handler=str,
        force_ascii=False)
    )

    ser_to_json = curry(lambda ser: ser.to_json(
        default_handler=str,
        force_ascii=False,
    ))


    def df_to_dict(df):
        return df.to_dict(orient='records') if isinstance(df, pd.DataFrame) else df.to_dict()


    TYPE_REGS = (
        (is_a(pd.DataFrame), lambda df: flat_concat(df.to_dict(orient='records'))),
        (is_a(pd.Series), lambda ser: flat_concat(ser.to_dict())),
        (is_a(np.bool_), bool),
    )

    __all__ = (
        'col_value',
        'df_dt',
        'df_to_json',
        'ser_to_json',
        'df_to_dict',
        'TYPE_REGS',
    )
except ModuleNotFoundError:
    TYPE_REGS = ()
    __all__ = ('TYPE_REGS',)
