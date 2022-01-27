import pandas as pd
from dateutil.parser import parse

value_counts = []
VALID_TYPES = [pd.DataFrame]

def cat_unique_counts(df):
    """
    Return unique value count of categorical features
    
    Parameters
    ----------
    df: pd.DataFrame
        pandas dataframe

    Returns
    -------
    pd.DataFrame

    Examples
    --------
    >>>from slimeda import cat_unique_counts
    >>>cat_unique_counts(df)
    """
    # check the type of data input
    if not isinstance(df, pd.DataFrame) :
        raise TypeError("Please provide a pd.DataFrame for the 'df' argument")
    
    if len(df) == 0 :
        return None

    # get only object data types
    _cat_feats = df.select_dtypes(include=['object'], 
                        exclude= ['int64','float64', 'datetime']).columns

    # get categorical features only
    df_str = df[_cat_feats]

    # check if any categorical features looks like a date
    df_is_date = df_str[df_str.columns.tolist()].applymap(_is_date).any()

    # get features name that don't look like a date
    cat_feats = list(df_is_date[df_is_date == False].index)

    features = list(cat_feats)

    # get unique value count of every categotical feature
    for feature in features:
        value_counts.append(len(df[feature].unique()))

    # zip feature name and value_count as a dictionary
    df_cat_unique = list(zip(features, value_counts))

    # make them a dataframe
    df_cat_unique = pd.DataFrame(df_cat_unique, columns=['feature name', 'unique count'])
    return df_cat_unique


# Helper function
def _is_date(string):
    """
    Check if a string can be parsed as a date
    Parameters
    ----------
    string : str
            string value
    Returns
    -------
    bool
    Examples
    --------
    >>>_is_date('2022-01-13')
    """
    try:
        parse(string)
        return True
    except ValueError:
        return False