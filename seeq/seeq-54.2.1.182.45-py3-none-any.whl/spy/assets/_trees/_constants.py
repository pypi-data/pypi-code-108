import pandas as pd

reference_types = ['StoredSignal', 'StoredCondition']
calculated_types = ['CalculatedScalar', 'CalculatedSignal', 'CalculatedCondition']
data_types = calculated_types + reference_types
supported_input_types = data_types + ['Asset']
supported_output_types = calculated_types + ['Asset']

dataframe_dtypes = {
    'ID': str,
    'Referenced ID': str,
    'Path': str,
    'Name': str,
    'Type': str,
    'Depth': int,
    'Description': str,
    'Formula': str,
    'Formula Parameters': (str, list, dict, pd.Series, pd.DataFrame),
    'Cache Enabled': bool
}
dataframe_columns = list(dataframe_dtypes.keys())

MAX_ERRORS_DISPLAYED = 3
