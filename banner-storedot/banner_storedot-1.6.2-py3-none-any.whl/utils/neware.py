from functools import reduce

import pandas as pd
import numpy as np
from pandas.core.computation.ops import UndefinedVariableError

from banner.utils.const import (
    NW_VOLTAGE, NW_CURRENT, NW_TEMP, NW_AUX_CHANNEL, NW_STEP_RANGE, 
    NW_TIMESTAMP, NW_DATESTAMP, NW_CHANNEL_GROUP, NW_SEQ, 
    NW_CACHE_CYCLE_SEQ, NW_UNIT, NW_CHANNEL, NW_TEST,
    PREV_SUFFIX, OUTLIER_STD_COEFFECIENT,
    NW_CACHE_MERGED_COLUMNS, NW_CACHE_DUR
)

from banner.utils.pandas import assert_required_columns, parse_mysql_to_pandas_query

def calculate_neware_columns(df: pd.DataFrame, temperature=True, cache_df: pd.DataFrame = pd.DataFrame()):
    ''' 
        Assures df is sorted by seq_id
        Performs calculate_voltage, calculate_current, calculate_neware_timestamp
        If temperature performs calculate_temperature, group_by_auxchl
        cache_df can be used to calculate_neware_timestamp
        Raises KeyError for missing columns
    '''
    assert_required_columns(df, NW_SEQ)
    
    df = df.copy()

    df = df.sort_values([NW_SEQ])
    
    df[NW_VOLTAGE] = calculate_voltage(df)
    df[NW_CURRENT] = calculate_current(df)
    
    df[NW_TIMESTAMP] = calculate_neware_timestamp(df, cache_df=cache_df)
    
    if temperature:
        df[NW_TEMP] = calculate_temperature(df)
        df = group_by_auxchl(df)
        
    return df

def group_by_auxchl(df: pd.DataFrame):
    ''' 
        Group by auxchl_id set test_temp to auxchl_num
    '''
    merge_columns = [column for column in list(df.columns) if column not in [NW_TEMP, NW_AUX_CHANNEL]]
    
    assert_required_columns(df, NW_TEMP, NW_AUX_CHANNEL)

    # groupby -> to list & rename NW_AUX_CHANNEL
    group_as_list = [
        _df.loc[
            :, _df.columns != NW_AUX_CHANNEL
        ].rename(columns={NW_TEMP: f'{NW_CHANNEL_GROUP}{group}'})
        for group, _df in df.groupby([NW_AUX_CHANNEL])
    ]
    
    # Merge 
    merged_data = reduce(lambda left,right: pd.merge(left, right, on=merge_columns, how='left'), group_as_list)

    return merged_data

def calculate_temperature(df: pd.DataFrame):
    ''' 
        Calculate temp from test_temp
    '''
    assert_required_columns(df, NW_TEMP)
    
    return df[NW_TEMP].apply(lambda obj: obj / 10)
    
def calculate_voltage(df: pd.DataFrame):
    ''' 
        Calculate voltage from test_vol
    '''
    assert_required_columns(df, NW_VOLTAGE)

    return df[NW_VOLTAGE].apply(lambda obj: obj / 10000)

def calculate_current(df: pd.DataFrame):
    ''' 
        Calculate current from test_cur
    '''
    assert_required_columns(df, NW_CURRENT, NW_STEP_RANGE)

    return df.apply(lambda row: round(row[NW_CURRENT] * __current_coeff(row[NW_STEP_RANGE]), 4), axis=1)

def calculate_neware_timestamp(df: pd.DataFrame, cache_df: pd.DataFrame = pd.DataFrame()):
    ''' 
        Calculate timestamp using test_time, seq_id
    '''
    required_columns = [NW_SEQ, NW_TIMESTAMP]

    assert_required_columns(df, *required_columns)

    _df = df[required_columns]
    
    try: #Try to create cached cycle_end_seq to calculate_neware_timestamp
        __cached_cycle_end_seq = pd.Series(data=cache_df[NW_CACHE_DUR].values, index=cache_df[NW_CACHE_CYCLE_SEQ].values)
        
    except (TypeError, KeyError):
        __cached_cycle_end_seq = pd.Series()
    
    prev_timestamp, prev_seq_id = NW_TIMESTAMP + PREV_SUFFIX, NW_SEQ + PREV_SUFFIX
    
    # Remove chained_assignment warning
    __chained_assignment = pd.options.mode.chained_assignment
    pd.options.mode.chained_assignment = None

    # Add prev test_time and prev seq_id to _df
    _df[prev_timestamp] = _df[NW_TIMESTAMP].shift(1)
    _df[prev_seq_id] = _df[NW_SEQ].shift(1)
    
    # Restore chained_assignment warning
    pd.options.mode.chained_assignment = __chained_assignment
    
    # prev test_time and seq_id where current test_time = 0 (all step and cycle ends)
    __cycle_end_seq = _df.loc[
        _df[NW_TIMESTAMP] == 0, 
        [prev_seq_id, prev_timestamp]
    ]
    
    # Create cycle_end_seq of given df
    __cycle_end_seq = pd.Series(data=__cycle_end_seq[prev_timestamp].values, index=__cycle_end_seq[prev_seq_id].values)
    
    # Combine them and sum of prev (combine cache_df into df)
    __cycle_end_seq = __cycle_end_seq.combine_first(__cached_cycle_end_seq).dropna().cumsum()
    
    def __calc_timestamp(row):
        try:
            steps = __cycle_end_seq[__cycle_end_seq.index < row[NW_SEQ]] #Get all sum of steps before row seq_id
            last_step = steps.iloc[-1] # Pick last one
    
            return row[NW_TIMESTAMP] + last_step # Append current + sum of last step

        except (IndexError, AssertionError):
            return row[NW_TIMESTAMP]
    
    timestamps = _df.apply(lambda row: __calc_timestamp(row), axis=1)
    
    return timestamps

def __current_coeff(cur_range):
    return 0.00001 * 10**min(4, len(str(cur_range))) * (0.1 if cur_range < 0 else 1)
    
def calculate_dqdv(df: pd.DataFrame, raw=False):
    ''' 
        Calculate DQ/DV for a valid neware df
        raw=False: remove outliers
    '''
    required_columns = [NW_VOLTAGE, NW_CURRENT, NW_TIMESTAMP]

    assert_required_columns(df, *required_columns)
    
    _df = df.copy()
    
    _df = df[required_columns]

    dt = _df[NW_TIMESTAMP] - _df[NW_TIMESTAMP].shift(1)
    
    dv = _df[NW_VOLTAGE] - _df[NW_VOLTAGE].shift(1)
    
    current = _df[NW_CURRENT]
        
    dq = current * dt / 1000 / 3600
    
    dqdv = dq / dv

    if not raw:
        dqdv.replace([np.inf, -np.inf], np.nan, inplace=True)
        
        dqdv[(np.abs(dqdv - dqdv.mean()) > (OUTLIER_STD_COEFFECIENT * dqdv.std()))] = np.nan
        
    return dqdv

def merge_cache(df: pd.DataFrame, cache_df: pd.DataFrame):
    ''' 
        Merge neware dataframe(data)
        With neware cache dataframe(cache_data)
        Raises TypeError, IndexError for bad input
    '''
    merged_columns = [NW_UNIT, NW_CHANNEL, NW_TEST]
    neware_required_columns = merged_columns + [NW_SEQ]
    neware_cache_required_columns = merged_columns + [NW_CACHE_CYCLE_SEQ]

    if not isinstance(df, pd.DataFrame) or not all(col in df for col in neware_required_columns):
        raise TypeError(f'Merging requires Neware DataFrame with {NW_SEQ} columns')

    if not isinstance(cache_df, pd.DataFrame) or not all(col in cache_df for col in neware_cache_required_columns):
        raise TypeError(f'Merging requires Neware Cache DataFrame with {NW_CACHE_CYCLE_SEQ} columns')
    
    # if not all((df[column].unique() == cache_df[column].unique()).all() for column in merged_columns):
    #     raise IndexError(f'Merging must have {merged_columns} columns with similar unique values!')

    CACHE_SEQ_RANGE = [0] + list(cache_df[NW_CACHE_CYCLE_SEQ]) + [np.inf]
    
    def __merge_cache(group):
        try:
            cache_row = cache_df[cache_df[NW_CACHE_CYCLE_SEQ] == group.name.right].iloc[-1]
            
            for col in NW_CACHE_MERGED_COLUMNS:
                group[col] = cache_row[col]
            
        except IndexError:
            for col in NW_CACHE_MERGED_COLUMNS:
                group[col] = None
            
        return group
    
    df = df.groupby(
        pd.cut(
            df[NW_SEQ], 
            CACHE_SEQ_RANGE
        )
    ).apply(__merge_cache)
    
    return df

def query_cache(df: pd.DataFrame, query: str):
    ''' 
        Query df and returnes seq_id ranges
    '''
    try:
        df_by_query = df.query(
            parse_mysql_to_pandas_query(query)
        )
        
        ranges = [__query_cache_by_group(df, group_by_query) for index, group_by_query in df_by_query.groupby(df_by_query.index.to_series().diff().ne(1).cumsum())]
        
        assert(ranges)

        return f'({" OR ".join(ranges)})' 

    except AssertionError:
        return '0'

    except (UndefinedVariableError, SyntaxError, TypeError, ValueError):
        return query  

def __query_cache_by_group(df: pd.DataFrame, group: pd.DataFrame):
    first_seq_id = 0
    
    if group.index[0] > 0:
        first_seq_id = df.iloc[group.index[0] - 1][NW_CACHE_CYCLE_SEQ]
    
    last_seq_id = group.iloc[-1][NW_CACHE_CYCLE_SEQ]
    
    return f'{NW_SEQ} > {first_seq_id} AND {NW_SEQ} <= {last_seq_id}'