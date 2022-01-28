import pandas as pd
import numpy as np
def outlier_identifier(dataframe, columns=None, identifier = 'IQR', return_df=False):
    """
    A function that identify and summarize the count and range of based on the method the user choose
    Parameters
    ----------
    dataframe : pandas.core.frame.DataFrame
        The target dataframe where the function is performed.
    columns : list, default=None
        The target columns where the function needed to be performed. Default is None, the function will check all columns
    identifier : string, default='IQR'
        The method of identifying outliers.
        - if "Z_score" : Use z-test with threshold of 3
        - if "IQR" : Use IQR (Inter Quantile range) to identify outliers (default)
    return_df : bool, default=False
        Can be set to True if want output as dataframe identified with outliers in rows

    Returns
    -------
    pandas.core.frame.DataFrame 
    (a dataframe with the summary of the outlier identified by the method) if return_df = False , 
    (a dataframe with additional column having if row has outlier or not) if return_df = True
    
    Examples
    --------
    >>> import pandas as pd
        
    >>> df = pd.DataFrame({
    >>>    'SepalLengthCm' : [5.1, 4.9, 4.7, 5.5, 5.1, 50, 54, 5.0, 5.2, 5.3, 5.1],
    >>>    'SepalWidthCm' : [1.4, 1.4, 20, 2.0, 0.7, 1.6, 1.2, 1.4, 1.8, 1.5, 2.1],
    >>>    'PetalWidthCm' : [0.2, 0.2, 0.2, 0.3, 0.4, 0.5, 0.5, 0.6, 0.4, 0.2, 5]
    >>> })
    >>> outlier_identifier(df)
    	                SepalLengthCm SepalWidthCm PetalWidthCm
    outlier_count                  2            1            1
    outlier_percentage        18.18%        9.09%        9.09%
    mean                       13.63         3.19         0.77
    median                       5.1          1.5          0.4
    std                        18.99         5.59         1.41
    lower_range                  NaN          NaN          NaN
    upper_range         (50.0, 54.0)         20.0          5.0
    """

    # Handle dataframe type error (Check if dataframe is of type Pandas DataFrame)
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError(f"passed dataframe is of type {type(dataframe).__name__}, should be DataFrame")
        
    # Handle empty dataframe or dataframe with all NAN
    if dataframe.empty or dataframe.dropna().empty:
        raise ValueError("passed dataframe is None")
    
    # Handle columns type error (Check if columns are None or type list)
    if not columns is None and not isinstance(columns, list):
        raise TypeError(f"passed columns is of type {type(columns).__name__}, should be list or NoneType")
    
    # Handle identifier type error (Check if identifier is of type str)
    if not isinstance(identifier, str):
        raise TypeError(f"passed identifier is of type {type(identifier).__name__}, should be string with value 'Z_score' or 'IQR'")
    
    # Handle identifier Value error (Check if identifier has value 'Z_score' or 'IQR')
    if identifier!='Z_score' and identifier!='IQR':
        raise ValueError("passed identifier should have value 'Z_score' or 'IQR'")
        
    # Handle return_df type error (Check if identifier is of type bool)
    if not isinstance(return_df, bool):
        raise TypeError(f"passed return_df is of type {type(return_df).__name__}, should be bool with value as True or False")

    if columns is None:
        columns = dataframe.columns
    df_filtered = dataframe[columns]
    numeric_columns = df_filtered.select_dtypes('number').columns
    df_selected = df_filtered[numeric_columns]
    df_selected['outlier'] = False
    
    output = pd.DataFrame(columns=numeric_columns, index=['outlier_count', 'outlier_percentage', 'mean', 'median', 'std', 'lower_range', 'upper_range'])
    if identifier == 'Z_score':
        if return_df == False:
            for col in numeric_columns:
                std = df_selected[col].std()
                mean = df_selected[col].mean()
                col_outliers = df_selected[np.abs(df_selected[col] - mean) > std*3]
                output.loc['outlier_count', col] = len(col_outliers)
                output.loc['outlier_percentage', col] = str(round(len(col_outliers) * 100 / len(df_selected), 2)) + '%'
                output.loc['mean', col] = round(mean, 2)
                output.loc['median', col] = round(np.percentile(df_selected[col], 50), 2)
                output.loc['std', col] = round(std, 2)

                low_range = col_outliers[col_outliers[col] < -std*3]
                if not low_range.empty:
                    if len(low_range) == 1:
                        output.loc['lower_range', col] = min(low_range[col])
                    else:
                        output.loc['lower_range', col] = (min(low_range[col]), max(low_range[col]))
                upper_range = col_outliers[col_outliers[col] > std*3]
                if not upper_range.empty:
                    if len(upper_range) == 1:
                        output.loc['upper_range', col] = min(upper_range[col])
                    else:
                        output.loc['upper_range', col] = (min(upper_range[col]), max(upper_range[col]))
            return output
        else:
            for col in numeric_columns:
                std = df_selected[col].std()
                mean = df_selected[col].mean()
                df_selected.loc[np.abs((df_selected[col] - mean)) > std*3, 'outlier'] = True
            return df_selected


    elif identifier == 'IQR':
        if return_df == False:
            for col in numeric_columns:
                std = df_selected[col].std()
                mean = df_selected[col].mean()
                iqr = np.percentile(df_selected[col], 75) - np.percentile(df_selected[col], 25)
                col_outliers = df_selected[np.abs((df_selected[col] - mean) / std) > 1.5*iqr]
                output.loc['outlier_count', col] = len(col_outliers)
                output.loc['outlier_percentage', col] = str(round(len(col_outliers) * 100 / len(df_selected), 2)) + '%'
                output.loc['mean', col] = round(mean, 2)
                output.loc['median', col] = round(np.percentile(df_selected[col], 50), 2)
                output.loc['std', col] = round(std, 2)
                low_range = col_outliers[col_outliers[col] < -1.5*iqr]
                if not low_range.empty:
                    if len(low_range) == 1:
                        output.loc['lower_range', col] = min(low_range[col])
                    else:
                        output.loc['lower_range', col] = (min(low_range[col]), max(low_range[col]))
                upper_range = col_outliers[col_outliers[col] > 1.5*iqr]
                if not upper_range.empty:
                    if len(upper_range) == 1:
                        output.loc['upper_range', col] = min(upper_range[col])
                    else:
                        output.loc['upper_range', col] = (min(upper_range[col]), max(upper_range[col]))
            return output

        else:
            for col in numeric_columns:
                std = df_selected[col].std()
                mean = df_selected[col].mean()
                iqr = np.percentile(df_selected[col], 75) - np.percentile(df_selected[col], 25)
                df_selected.loc[np.abs((df_selected[col] - mean) / std) > 1.5*iqr, 'outlier'] = True
            
            return df_selected