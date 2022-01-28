import pandas as pd
from modelify.schema import InputList, Input, InputType

def create_schema(data, pipeline=False) -> InputList:
    
    if isinstance(data, pd.DataFrame):
        if pipeline:
            return InputList(
                [Input(input_type=pandas_column_to_type(data[col]), name=col) for col in data.columns]
            )
        else:
            return InputList(
                [Input(input_type=InputType.float, name=col) for col in data.columns]
            )
    else:
        raise Exception("Expected pandas.DataFrame, got '{}'".format(type(data)))
        

def pandas_column_to_type(col: pd.Series) -> InputType:
    if not isinstance(col, pd.Series):
        raise TypeError("Expected pandas.Series, got '{}'.".format(type(col)))
    if len(col.values.shape) > 1:
        raise Exception("Expected 1d array, got array with shape {}".format(col.shape))

    if pd.api.types.is_string_dtype(col):
        return InputType.string
    elif col.dtype.kind == "b":
        return InputType.boolean
    elif col.dtype.kind == "i" or col.dtype.kind == "u":
        if col.dtype.itemsize < 4 or (col.dtype.kind == "i" and col.dtype.itemsize == 4):
            return InputType.integer
        elif col.dtype.itemsize < 8 or (col.dtype.kind == "i" and col.dtype.itemsize == 8):
            return InputType.long
    elif col.dtype.kind == "f":
        return InputType.float
    elif col.dtype.kind == "U":
        return InputType.string
    raise Exception("Unsupported numpy data type '{0}', kind '{1}'".format(col.dtype, col.dtype.kind))
