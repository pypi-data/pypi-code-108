import logging
import pandas as pd
from typing import List
import re
# List all files in a database
# List all files matching a certain pattern


logger = logging.getLogger("preprocessing_helper")

def flatten_mutli_index(input_df_cols:List)->List:
    """Flattens a hierachichal pandas index

    Args:
        input_df_cols (List): List type object of hierachical indices

    Returns:
        List: Flatten list of indexes where the index names are concatonated 
        by _
    """
    input_df_cols = [re.sub("_$", "", '_'.join(col).strip()) 
                     for col in input_df_cols]
    return input_df_cols
    

def pd_safe_merge(input_df_1:pd.DataFrame, input_df_2:pd.DataFrame, *args, 
                  raise_exception:bool=False, **kwargs)->pd.DataFrame:
    """Wrapper for pandas merge but raises a warning (and optionally an 
    exception) when the row counts have been altered by the merge

    Args:
        input_df_1 (pd.DataFrame): Input dataframe whichh requires merging. 
        This dataframe will be used as the basis for the row counts
        input_df_2 (pd.DataFrame): Input dataframe whichh requires merging. 
        raise_exception (bool, optional): Indicator determining whether an 
        exception should be raised if the row counts don't match. Defaults to 
        False.

    Raises:
        Exception: Raised when the row counts don't match and raise_exception 
        is True

    Returns:
        pd.DataFrame: pandas data frame with input_df_1 and input_df_2 joined
    """
    pre_join_shape = input_df_1.shape[0]
    out_df = pd.merge(input_df_1, input_df_2, *args, **kwargs)
    if pre_join_shape != out_df.shape[0]:
        warn_msg = "Join has altered the shape of input_df_1."
        logger.warning(warn_msg)
        info_msg = "input_df_1 shape: {}, input_df_2 shape: {}, out_df shape: {}".format(
            input_df_1.shape[0], input_df_2.shape[0], out_df.shape[0])
        logger.info(info_msg)
        if raise_exception:
            raise Exception(warn_msg+" "+info_msg)
    else:
        pass
    return out_df