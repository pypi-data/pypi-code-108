import pandas as pd

def calculate_stat_summary(df, data_type='cases'):
    """Creates summary information about the 
       covid cases in each province of Canada

    Parameters
    ----------
    df : pandas.DataFrame
        Pandas DataFrame containing covid data to summary.
    data_type : string, default='cases'
        A string, specifying which kind of data the dataframe contains.
        the data_type must be in:
        ['cases', 'mortality', 'recovered', 'testing', 'active', 'dvaccine', 'avaccine', 'cvaccine']

    Returns
    -------
    pandas.DataFrame
        pandas DataFrame containing summary information.

    Examples
    --------
    >>> calculate_stat_summary(covid_df, 'active')
    >>> calculate_stat_summary(covid_df)
    """
    # Check data_type validity
    stat_types = ['cases', 'mortality', 'recovered', 'testing', 'active', 'dvaccine', 'avaccine', 'cvaccine']
    if not isinstance(data_type, str):
        raise TypeError("Invalid argument type: data_type must be a string")
    elif data_type not in stat_types:
        raise ValueError("Stat type must be within pre-defined options.\
                        Choose from: ['cases', 'mortality', 'recovered',\
                        'testing', 'active', 'dvaccine', 'avaccine', 'cvaccine']")

    # Choose the date column and the column to summarize
    date_col = ''
    summ_col = ''
    if data_type == 'cases':
        date_col = 'date_report'
        summ_col = 'cases'
    elif data_type == 'mortality':
        date_col = 'date_death_report'
        summ_col = 'deaths'
    elif data_type == 'recovered':
        date_col = 'date_recovered'
        summ_col = 'recovered'
    elif data_type == 'testing':
        date_col = 'date_testing'
        summ_col = 'testing'
    elif data_type == 'active':
        date_col = 'date_active'
        summ_col = 'active_cases'
    elif data_type == 'dvaccine':
        date_col = 'date_vaccine_distributed'
        summ_col = 'dvaccine'
    elif data_type == 'avaccine':
        date_col = 'date_vaccine_administered'
        summ_col = 'avaccine'
    elif data_type == 'cvaccine':
        date_col = 'date_vaccine_completed'
        summ_col = 'cvaccine'
        
    # Check input dataframe validity
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Invalid argument type: df must be a pandas DataFrame")
    elif len(df) == 0:
        raise ValueError("Argument value error: df must contain at least one row of data")
    elif not ((date_col in df.columns) and ('province' in df.columns)):
        raise ValueError(f"Argument value error: df must contain {date_col} and province columns")

    # Select the up to date information of each province
    df[date_col] = pd.to_datetime(df[date_col], format='%d-%m-%Y')
    max_date = df.loc[df[date_col].argmax(), date_col]
    columns = [date_col, 'province'] + list(set(df.columns) - set([date_col, 'province']))
    summary = df[df[date_col] == max_date][columns].sort_values('province')

    # Summarize the min, max and mean of the selected summary column
    min_value = []
    max_value = []
    mean_value = []
    for i in range(len(summary)):
        province = summary.iloc[i, 1]
        min_value.append(int(df[df['province'] == province][summ_col].describe()[3]))
        max_value.append(int(df[df['province'] == province][summ_col].describe()[7]))
        mean_value.append(int(df[df['province'] == province][summ_col].describe()[1]))

    summary[summ_col + '_min'] = min_value
    summary[summ_col + '_max'] = max_value
    summary[summ_col + '_mean'] = mean_value

    return(summary)
