import pandas as pd
import time
from datetime import datetime
from typing import Union


def _detect_numeric_date_column(data_series: pd.Series, _year_reduced: int, _year_added: int) ->Union[str, None]:
    """
    Detects whether the given Series with numeric data type contains UNIX or year values.
    _year_reduced is subtracted from the current year to get the minimum threshold for detection.
    _year_added is added to the current year to get the maximum threshold for detection.
    Returns Series name, if contains UNIX or year.

    Args:
        data_series (pd.Series): Data series for detection.
        _year_reduced (int): Number to be subtracted.
        _year_added (int): Number to be added.

    Returns:
        Union[str, None]: Series name or None.
    """

    dt = datetime(datetime.today().year - _year_reduced, 1, 1).timestamp()
    dt_max = datetime(1970 + _year_added, 1, 1).timestamp()
    min_ = data_series.min()
    max_ = data_series.max()

    if min_ >= datetime.today().year-_year_reduced and max_ <= datetime.today().year + _year_added:

        return data_series.name

    elif min_ >= dt * 1_000 and max_ <= (time.time() + dt_max) * 1_000:

        return data_series.name

    elif min_ >= dt and max_ <= time.time() + dt_max:

        return data_series.name

    
def get_datetime_columns(data: pd.DataFrame, _year_reduced: int=40, _year_added: int=20, time_col_thresh: float=None) -> tuple:
    """
    Gets a data table and identifies the date/time type columns.
    Object columns are detected using pd.to_datetime function.
    _detect_numeric_date_column function is used for detecting the numeric columns.

    Args:
        data (pd.DataFrame): Data table for date/time columns identification.
        _year_reduced (int): Number to be subtracted. Defaults to 40.
        _year_added (int): Number to be added. Defaults to 20.
        time_col_thresh (float): Threshold to identify if a column with mixed values can be datetime. The lower the threshold the stricter is criterion. Defaults to 0.35.
        logger (Logger, optional): Instance of a logger class to log calculations. Defaults to None.

    Returns:
        list: List of identified date column names.
        list: List of possible date column names, which have mixed types.

    Examples:
        >>> data = pd.DataFrame({"date_column": ["02-january-1978", "29-march-1978"]})
        >>> date_columns, possible_date_columns  = get_datetime_columns(data)
        >>> print(date_columns, possible_date_columns)
    """
    time_col_thresh = 0.35

    possible_time_cols = []
    time_cols = []
    for col in data:
        if data[col].dtypes == object:
            try:
                data_series = data[col].astype(float)
                col = _detect_numeric_date_column(data_series, _year_reduced, _year_added)
                if col:
                    time_cols.append(col)
            except ValueError:
                try:
                    _ = pd.to_datetime(data[col], errors='raise')
                    time_cols.append(col)
                except:
                    candidate = pd.to_datetime(data[col], errors="coerce")
                    if candidate.isnull().sum() / data[col].shape[0] < time_col_thresh:
                        if candidate.mode()[0] > pd.to_datetime("1972-01-01"):
                            possible_time_cols.append(col)
                    pass
        elif data[col].dtypes == '<M8[ns]':
            time_cols.append(col)
        else:
            col = _detect_numeric_date_column(data[col], _year_reduced, _year_added)
            if col:
                time_cols.append(col)


    return time_cols, possible_time_cols


def _get_text_columns(data: pd.DataFrame) -> list:
    """
    Takes the data and identifies text containing columns.
    If there are on average more than 4 space separated words in the values of object column then assigns it as a text column.

    Args:
        data (pd.DataFrame): Data table.

    Returns:
        list: List with text column names.
    """

    text_cols = []
    d_types = data.dtypes
    for col in d_types[d_types=="object"].index:
        uniques = data[col].nunique()

        avg = data[col].dropna().apply(lambda x: len(str(x).split(" "))).mean()
        
        if avg < 1.5:
            continue
        if avg > 4 or uniques > 60:
            text_cols.append(col)

    return text_cols


def _get_id_columns_based_on_nunique(data: pd.DataFrame, thresh: float):
    """
    Gets the data and identifes id columns.
    If the ratio of the unique values of a column to their count is higher then the given threshold, assigns the column as id.

    Args:
        data (pd.DataFrame): Data table.
        thresh (float): Threshold for id identification.

    Returns:
        list: List with id column names.
    """

    id_cols = []
    for col in data:
        if data[col].nunique()/data.shape[0] > thresh and not data[col].dtype == float:
            id_cols.append(col)

    return id_cols


def _get_id_columns_based_on_name(data: pd.DataFrame):
    """
    Gets the data and identifes id columns.
    Cleans the column names with ColumnCleaner module then makes columns lowercase.
    If there is "id" unit in the column name, assigns it as id.

    Args:
        data (pd.DataFrame): Data table.

    Returns:
        list: List with id column names.
    """

    # cc = ColumnCleaner()
    # cc.fit(data)
    # data_ = cc.transform(data)
    cols = data.columns.tolist()
    # id_names = [x for x in cols if "id" in x.lower().split("_")]
    # id_names = [x for x in cc.mapping_dict if cc.mapping_dict[x] in id_names]

    id_names = [x for x in cols if "id" in x.lower().split("_")]

    return id_names


def get_column_types(data: pd.DataFrame, num_unique_categories: int=None, id_thresh: float=None) -> dict:
    """
    Takes the dataframe and the parameter for unique categories and id threshold.
    Identifes date columns with get_datetime_columns.
    Identifies id column with the union of _get_id_columns_based_on_nunique and _get_id_columns_based_on_name.
    Selects the columns, which unique values are lower than or equal to the parameter, as categorical.
    Separates the binary value containing columns from categorical columns.
    The rest of the columns turns to numeric, drops the ones which fail during the process.
    Separates the columns with one unique class and the ones which fail to convert to numeric, for dropping.

    Args:
        data (pd.DataFrame): Data table.
        num_unique_categories (int, optional): Unique categories threshold. If None, takes the default value of 60. Defaults to None.
        id_thresh (float, optional): Id threshold. If None, takes the default value of 0.85. Defaults to None.
	logger (Logger, optional): Instance of a logger class to log calculations. Defaults to None.

    Returns:
        tuple: Returns a dictinonary with "remove_cols", "date_cols", "text_cols", "id_cols", "binary_cols", "cat_cols", "num_cols" as keys and respective list values.
    """

    num_unique_categories_def = num_unique_categories #Jarvis.get(['constants', 'min_class_count_to_be_continuous'], 60)
    id_thresh_def = 0.85 #Jarvis.get(['constants', 'threshold_to_be_id'], 0.85)
        
    if id_thresh is None:
        id_thresh = id_thresh_def
    if num_unique_categories is None:
        num_unique_categories = num_unique_categories_def
        
    # get time columns
    date_cols, possible_time_cols = get_datetime_columns(data)

    remaining = set(data.columns) - set(date_cols) - set(possible_time_cols)

    # text cols
    text_cols = _get_text_columns(data[list(remaining)])
    #print('text cols are', text_cols)
    remaining = remaining - set(text_cols)

    # id cols
    # id1 = _get_id_columns_based_on_nunique(data[list(remaining)], id_thresh)
    # id2 = _get_id_columns_based_on_name(data[list(remaining)])

    # id_cols = list(set(id1).union(set(id2)))

    # remaining = remaining - set(id_cols)

    # categorical, numeric and binary cols
    result = [[col, data[col].nunique(dropna=False)] for col in remaining]
    result = pd.DataFrame(result, columns=["col", "uniq"])

    unique_one_class = result[result.uniq == 1].col.tolist()

    result = result[result.uniq>1]

    binary_cols = result[result["uniq"] == 2]["col"].tolist()
    result_log = result["uniq"] <= num_unique_categories

    cat_cols = result[result_log]["col"].tolist()
    num_cols = result[~result_log]["col"].tolist()

    rem_list = []
    for col in num_cols:
        try:
            data[col] = data[col].astype(float)
        except ValueError:
            rem_list.append(col)

    rem_list = rem_list + unique_one_class + possible_time_cols

    num_cols = list(set(num_cols)-set(rem_list))
    col_types = {"remove_cols": rem_list, "datetime": date_cols, 'texts': text_cols, 'binary': binary_cols, 'categorical': cat_cols, 'numeric': num_cols}


    return col_types