import numpy as np
import pandas as pd
from scipy import stats

def clean_up(df):
    """Takes a dataframe object and returns a cleaned version 
     with rows containing any NaN values dropped. 
     Inspects the clean dataframe and prints a list of potential outliers for each explanatory variable, 
     based on the threshold distance of 3 standard deviations.
        Parameters
        ----------
        df : dataframe
            dataframe to be cleaned
    
        Returns
        -------
        df_clean
            same dataframe with all the NaN's removed
        Examples
        --------
        >>> df_clean = clean_up(df)
                
        '**The following potenital outliers were detected:**
        Variable X: 
        [ 300, 301, 500, 1000 ]
        Variable Y: 
        [ 6.42, 6.44, 58.52, 60.22 ]'
    
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("the input df must be pd.DataFrame type")
    
    # Drop any row that contains missing value and reset the index
    df_clean = df.dropna(axis=0, how='any').reset_index(drop=True)

    # Keep only numerical variables relevant for outlier detection
    num_df = df_clean.select_dtypes(['number'])
    
    # Create a dataframe that contains only the outliers
    outlier_df = num_df[(np.abs(stats.zscore(num_df)) > 3)] 

    # Prints out unique outlier values for each variable
    print("**The following potenital outliers were detected:**")
    for col in outlier_df:
        outliers = outlier_df[col].dropna()
        if len(outliers) != 0:
            print(f"Variable {col}: ")
            print(np.unique(outliers.values))

    # returns the clean dataframe with NaN values dropped
    return df_clean