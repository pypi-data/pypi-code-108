def missing_check(df, threshold = 0, by='column_name', ascending=True, return_missing_cols = False):

    import pandas as pd
    

    missing_value_df = pd.DataFrame({'column_name': df.columns,
                                     'percent_missing': df.isnull().sum() / len(df),
                                     'total_missing': df.isnull().sum()
                                    })
    
    missing_value_df.sort_values(by=by, ascending=ascending, inplace=True)
    columns_with_missing_values = missing_value_df[missing_value_df["percent_missing"] > threshold].reset_index(drop = True)
    print(columns_with_missing_values)

    if return_missing_cols == True:
        
        return columns_with_missing_values['column_name'].tolist()
    
    else:
        return None

