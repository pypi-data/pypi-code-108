# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from IPython.core.display import display, HTML
from pandas import DataFrame
import data_analytics.exploratory_data_analysis as eda


def print_dataframe_analysis_report(dataframe: DataFrame, name: str = 'dataframe', sample_size: int = 5) -> None:
    """
    Print an analysis report of the data frame. 
    - Show the top five rows of the data frame as a quick sample.
    - Show the data types of each column.
    - Report count of any duplicates.
    - Report count of any missing values.
    - Report any single value columns.
    :param dataframe: The data frame to be analysed
    :param name: The name of the data frame
    """
    display(HTML(f'<h4>{name}</h4>'))
    display(HTML(f'<p>Row, Column Count: {dataframe.shape}</p>'))
    display(HTML('<h5>Sample: Top five rows</h5>'))
    display(dataframe.sample(sample_size))
    display(HTML('<h5>Data Types</h5>'))
    display(dataframe.dtypes)
    display(HTML('<h5>Duplicates</h5>'))
    duplicate_rows_dataframe: DataFrame = dataframe[dataframe.duplicated()]
    display(
        HTML(f'<p>Number of duplicate rows: {duplicate_rows_dataframe.shape[0]}</p>'))
    display(HTML('<h5>Null Values</h5>'))
    print(dataframe.isnull().sum())
    display(HTML('<h5>Single Value Columns</h5>'))
    report_single_value_columns(dataframe)
    display(HTML('<h5>Columns: Unique value counts</h5>'))
    report_columns_unique_value_counts(dataframe)
    display(HTML('<h5>Outlier Analysis</h5>'))
    report_outliers_columns(dataframe)


def report_columns_unique_value_counts(dataframe: DataFrame) -> None:
    """
    Report the unique value counts for each column
    :param dataframe: DataFrame
    """
    html: str = '<ul>'
    for column in dataframe.columns:
        html += f'<li>The column "{column}" has {dataframe[column].nunique()} unique values.</li>'
    html += '</ul>'
    display(HTML(html))


def report_single_value_columns(dataframe: DataFrame) -> None:
    """
    Report any columns that have only one value
    :param dataframe: DataFrame
    """
    html: str = '<ul>'
    has_no_single_value_columns = True
    for column in dataframe.columns:
        if eda.is_single_value_column(dataframe, column):
            html += f'<li>The column `{column}` has only one value. Recommend removing.</li>'
            has_no_single_value_columns = False
    html += '</ul>'

    if(has_no_single_value_columns):
        display(HTML('<p>No single value columns found.</p>'))
    else:
        display(HTML(html))


def report_outliers_columns(dataframe: DataFrame) -> None:
    """
    Report any columns that have outliers
    :param dataframe: DataFrame
    """
    has_no_outlier_columns = True
    html: str = '<ul>'
    for column_label in dataframe.columns:
        if eda.is_numeric_data_type_column(dataframe[column_label]):
            outlier_count = eda.count_outliers(dataframe, column_label)
            if outlier_count > 1:
                html += f'<li>The column "{column_label}" has {outlier_count} outliers. Recommend removing outliers.</li>'
                has_no_outlier_columns = False
            elif outlier_count == 1:
                html += f'<li>The column "{column_label}" has {outlier_count} outlier. Recommend removing outlier.</li>'
                has_no_outlier_columns = False
    html += '</ul>'

    if(has_no_outlier_columns):
        display(HTML('<p>No columns with outliers found.</p>'))
    else:
        display(HTML(html))
