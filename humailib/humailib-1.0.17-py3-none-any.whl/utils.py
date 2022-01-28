import pandas as pd
import numpy as np
import plotly.express as px
import re
from multiprocessing import Pool
import unidecode

import warnings

from pandas.api.types import is_float_dtype, is_numeric_dtype, is_string_dtype
#from humailib.cloud_tools import GoogleBigQuery, GoogleCloudStorage


def instantiate_class(module_name, class_name):
    module = __import__(module_name, globals(), locals(), [class_name])
    class_ = getattr(module, class_name)
    
    return class_


"""
Column type definitions from the data dictionary.
    
https://humai.sharepoint.com/:w:/s/Platform/ET6ZzN-QgiJIpLdbVMkFz0oBe9_UOhSoau0Zvbo7HJ-5lQ?e=OxMlYv
"""
humai_table_field_types = {    
    'transactions' : {
        'datetime' : ['Datetime'],
        'string' : ['Transaction_ID','Branch_ID','Customer_ID','Status','Single_Item_Product_ID','Zip','Item_Types'],
        'float' : ['Total_Gross','Discount','Amount_Paid','Voucher_Amount'],
        'int' : ['Total_Num_Items_Purchased'],
        'bool' : ['Voucher_Used'],
    },
    'items' : {
        'datetime' : ['Datetime'],
        'string' : ['Transaction_ID','Product_ID','Name','Item_Type'],
        'float' : ['Price', 'Discount'],
        'int' : ['Quantity'],
    },
    'mailings' : {
        'datetime' : ['Send_Datetime'],
        'string' : ['Broadcast_ID','Campaign_ID'],
        'int' : ['Num_Customers']
    },
    'mailings_events' : {
        'datetime' : ['Activity_Datetime', 'Send_Datetime'],
        'string' : ['Broadcast_ID','Customer_ID','Activity','Description'],
    },
    'customers' : {
        'string' : ['Customer_ID','Email'],
    },
    'customer_ids' : {
        'string' : ['Customer_ID','Personifier','Person']
    },
    'products' : {
        'string' : ['Name','Product_ID','SKU','Item_Type'],
        'float' : ['Price'],
    },
    'customer_characteristics' : {
        'string' : ['Customer_ID']
    },
    'product_characteristics' : {
        'string' : ['Product_ID']
    },
    'predictions' : {
        'string' : ['Customer_ID'],
        'datetime' : ['Date'],
        #'float' : ['CLV'],
        #'int' : ['Time_Of_Day']
    },
    'customer_lifetime_value' : {
        'float' : ['CLV'],
        'string' : ['Customer_ID'],
    },
}

def transactions_check_basic_assumptions(df):
    
    assert len(df[df.Amount_Paid < 0]) == 0
    assert len(df[df.Total_Gross < 0]) == 0
    assert len(df[df.Discount > 0]) == 0
    assert len(df) == df.Transaction_ID.nunique()
    assert len(df[df.Customer_ID == '']) == 0
    assert len(df[df.Transaction_ID == '']) == 0
    assert len(df[df.Total_Gross < df.Amount_Paid]) == 0
    
    assert len(df[df.Total_Num_Items_Purchased <= 0]) == 0
    
    
def items_check_basic_assumptions(df):
    
    assert len(df[df.Product_ID == '']) == 0
    assert len(df[df.Price < 0]) == 0
    assert len(df[df.Discount > 0]) == 0
    assert len(df[df.Quantity <= 0]) == 0
    

def customers_check_basic_assumptions(df):

    assert len(df) == df.Customer_ID.nunique()
    assert len(df[df.Customer_ID == '']) == 0
    
    
def products_check_basic_assumptions(df):
    
    assert len(df[df.Product_ID == '']) == 0
    assert len(df) == df.Product_ID.nunique()
    assert len(df[df.Price < 0]) == 0
    
    
humai_table_checks = {
    'transactions' : transactions_check_basic_assumptions,
    'items' : items_check_basic_assumptions,
    'customers' : customers_check_basic_assumptions,
    'products' : products_check_basic_assumptions,
}


def check_table(df, table_type, hard_assert=True):
    
    print("Checking columns...")
    for _,cols in humai_table_field_types.get(table_type,[]).items():
        for c in cols:
            if c in df:
                print("  '{}' -> Exists".format(c))
            else:
                if hard_assert:
                    assert c in df, "  '{}' -> Missing!".format(c)
                else:
                    warnings.warn(
                        "  '{}' -> Missing!".format(c),
                        category=UserWarning, 
                        stacklevel=1
                    )
         
    if table_type in humai_table_checks:
        print("Checking basic assumptions...")
        humai_table_checks[table_type](df)
                
                
def percentage_match_stats(df1, col1, df2, col2):
    vals1 = set(df1[col1].to_numpy())
    vals2 = set(df2[col2].to_numpy())
    
    print(f"Number of unique '{col1}': {len(vals1)}, unique '{col2}': {len(vals2)}")
    prop = 100.0 * len(vals1.intersection(vals2)) / len(vals1)
    print("Proportion of '{}' found in '{}': {:.2f} %".format(col1, col2, prop))
    
    diff = list(vals1.difference(vals2))[:5]
    print("First 5 of the difference set: {}".format(diff))
    

def convert_table_columns(
    df, 
    table_type = 'transactions', 
    datetime_format='%Y-%m-%d %H:%M:%S'
):
    
    """
    Convert table column types to table column type definitions as specified in the data dictionary:
    
    https://humai.sharepoint.com/:w:/s/Platform/ET6ZzN-QgiJIpLdbVMkFz0oBe9_UOhSoau0Zvbo7HJ-5lQ?e=OxMlYv
    """
    
    types = humai_table_field_types[table_type]
    if 'datetime' in types:
        columns_as_datetime(df, columns=types['datetime'], datetime_format=datetime_format)
    if 'string' in types:
        columns_as_str(df, columns=types['string'], uppercase=False, drop_empty=False)
    if 'float' in types:
        columns_as_float(df, columns=types['float'], na_replace_value=None, drop_na=False)
    if 'int' in types:
        columns_as_int(df, columns=types['int'], na_replace_value=None, drop_na=False)

    for c in df.columns: print("  {} -> {}".format(c, df[c].dtype))
        
        
def load_table(
    gbq, 
    dataset_table,
    table_type,
    datetime_columns = None,
    datetime_format = '%Y-%m-%d %H:%M:%S', 
    check_columns = True,
    flush_cache = True,
):
    """
    Load table and convert column types
    """    
         
    print("[load_table] Loading table...")
    df = gbq.download_table_to_pandas(dataset_table, flush_cache=flush_cache)

    if df is None:
        return None
    
    print("[load_table] Converting table columns...")
    if datetime_columns is not None:
        columns_as_datetime(df, columns=datetime_columns, datetime_format=datetime_format)
      
    
    if table_type is not None:
        
        do_continue = True
        if check_columns:
            for _,columns in humai_table_field_types[table_type].items():
                for c in columns:
                    if c not in df:
                        warnings.warn(
                            f"[load_table] Column {c} is missing...",
                            category=UserWarning, 
                            stacklevel=1
                        )
                        do_continue = False

        if not do_continue:
            return None

        convert_table_columns(df, table_type=table_type, datetime_format=datetime_format)    

        if table_type == 'transactions' and keep_most_recent_trans_id:
            print("[load_and_merge_tables] Keeping only the most recent Transaction ID, if there's multiples...")
            print("[load_and_merge_tables]   {:,} rows total.".format(len(df)))
            keep_most_recent_transaction_id(df)
            print("[load_and_merge_tables]   {:,} rows left.".format(len(df)))

    return df


def load_csv(
    gcs,
    filename,
    table_type,
    datetime_columns = None,
    datetime_format='%Y-%m-%d %H:%M:%S',
    check_columns=True,
    flush_cache = True
):
    """
    Load CSV from GCS and convert column types.
    """
    
    print("[load_table] Loading table...")
    df = gcs.download_csv(filename, flush_cache=flush_cache)
    
    if df is None:
        return None
    
    print("[load_table] Converting table columns...")
    if datetime_columns is not None:
        columns_as_datetime(df, columns=datetime_columns, datetime_format=datetime_format)
        
    if table_type is not None:
        
        do_continue = True
        if check_columns:
            for _,columns in humai_table_field_types[table_type].items():
                for c in columns:
                    if c not in df:
                        warnings.warn(
                            f"[load_table] Column {c} is missing...",
                            category=UserWarning, 
                            stacklevel=1
                        )
                        do_continue = False

        if not do_continue:
            return None
        
        convert_table_columns(df, table_type=table_type, datetime_format=datetime_format)
    
        if table_type == 'transactions' and keep_most_recent_trans_id:
            print("[load_and_merge_tables] Keeping only the most recent Transaction ID, if there's multiples...")
            print("[load_and_merge_tables]   {:,} rows total.".format(len(df)))
            keep_most_recent_transaction_id(df)
            print("[load_and_merge_tables]   {:,} rows left.".format(len(df)))

    return df


def load_and_merge_tables(
    gbq, 
    dataset,
    table_type,
    date_ranges,
    table_name = None,
    datetime_columns = None,
    datetime_format = '%Y-%m-%d %H:%M:%S', 
    check_columns = True,
    keep_most_recent_trans_id=True,
    flush_cache = True,
):
    """
    1. Load tables by date range. 
    2. Remove duplicate rows.
    3. Convert column types
    """    
    
    print("[load_and_merge_tables] Loading tables...")
    df = None
    for date_range in date_ranges:
        
        if table_name is not None:
            table = "{}.{}_{}".format(dataset, table_name, date_range)
        else:
            table = "{}.{}_{}".format(dataset, table_type, date_range)

        df_tmp = gbq.download_table_to_pandas(
            table,
            flush_cache=flush_cache
        )
        if df_tmp is not None:
            if df is None:
                df = df_tmp.copy()
            else:
                df = df.append(df_tmp, sort=True, ignore_index=True)

    if df is None:
        return None
    
    do_continue = True
    if check_columns:
        for _,columns in humai_table_field_types[table_type].items():
            for c in columns:
                if c not in df:
                    warnings.warn(
                        f"[load_and_merge_tables] Column {c} is missing...",
                        category=UserWarning, 
                        stacklevel=1
                    )
                    do_continue = False
                    
    if not do_continue:
        return None
    
    print("[load_and_merge_tables] Dropping duplicate rows...")
    print("[load_and_merge_tables]   {:,} rows total.".format(len(df)))
    df.drop_duplicates(inplace=True)
    print("[load_and_merge_tables]   {:,} rows left.".format(len(df)))
    
    print("[load_and_merge_tables] Converting table columns...")
    if datetime_columns is not None:
        columns_as_datetime(df, columns=datetime_columns, datetime_format=datetime_format)
    convert_table_columns(df, table_type=table_type, datetime_format=datetime_format)
    
    if table_type == 'transactions' and keep_most_recent_trans_id:
        print("[load_and_merge_tables] Keeping only the most recent Transaction ID, if there's multiples...")
        print("[load_and_merge_tables]   {:,} rows total.".format(len(df)))
        keep_most_recent_transaction_id(df)
        print("[load_and_merge_tables]   {:,} rows left.".format(len(df)))
    
    return df


def upload_and_append_table_unique(
    gbq,
    dataset_table,
    df,
    unique_subset,
    datetime_columns=[],
    table_type=None,
    check_columns=False,
    flush_cache=True,
):
    df_existing = load_table(
        gbq,
        dataset_table,
        table_type=table_type,
        datetime_columns=datetime_columns,
        check_columns=check_columns,
        flush_cache=flush_cache,
    )
    
    if df_existing is not None:
    
        print(f"Size of existing table before appending: {len(df_existing):,}")
        df_existing = df_existing.append(df, sort=True, ignore_index=True)
        df_existing.drop_duplicates(subset=unique_subset, keep='first', inplace=True)
        print(f"Size of table after appending and removing duplicates: {len(df_existing):,}")
    
        gbq.upload_and_replace_table(
            df_existing,
            dataset_table,
        )
    else:
        gbq.upload_and_replace_table(
            df,
            dataset_table,
        )        

def merge_dataframes(dataframes, on, how='left', overwrite_cols=False):
    
    df_out = None
    for df in dataframes:
        if df_out is None:
            df_out = df
        else:
            if not overwrite_cols:
                cols_to_keep = [on] + [c for c in df.columns if c not in df_out]
                df_out = df_out.merge(
                    df[cols_to_keep],
                    on=on,
                    how='left',
                    copy=False,
                )
            else:
                for c in df.columns:
                    if c in df_out:
                        del df_out[c]
                df_out = df_out.merge(
                    df,
                    on=on,
                    how='left',
                    copy=False,
                )
                
    return df_out


def keep_most_recent_transaction_id(df, inplace=True):
    keep_most_recent_id(df, id_column='Transaction_ID', inplace=inplace)
    
    
def keep_most_recent_id(df, id_column='Transaction_ID', inplace=True):
    if not inplace:
        return df.rename_axis('_index').sort_values(by=[id_column,'Datetime','_index']).drop_duplicates(subset=id_column, keep='last')

    df.rename_axis('_index').sort_values(by=[id_column,'Datetime','_index'], inplace=True)
    df.drop_duplicates(subset=id_column, keep='last', inplace=True)
    
    
def force_string(value):
    return 'S' + str(value)#'S' + str(value)


def get_papermill_param(param, type_str='str', vis=None):
    
    if vis is None:
        vis = globals()
        
    var_lookup = {
        'int' : 0,
        'float' : 0.0,
        'list' : [],
        'dict' : {},
        'bool' : False,
        'str' : '',
    }

    value = var_lookup.get(type_str, None)
    if param in vis:
        
        value = vis[param] if vis[param] is not None else var_lookup.get(type_str, None)
        print("PAPERMILL -> Set '{}' to {}".format(
            param, value
        ))
            
    return value


def gbq_friendly_column_name(column):
    
    col_name = column
    if str.isdigit(col_name[0]):
        col_name = '_' + col_name
        
    return unidecode.unidecode(re.sub(r'[^\w]', '_', col_name).replace('-','_')).replace('+','plus').replace('-','to')


def bq_friendly_column_names(columns):

    return [gbq_friendly_column_name(c) for c in columns]
    

def column_stats(df, col_name, n=-1):
    """
    Print out column statistics.
    """
    
    print("-------------------------")
    print("COLUMN_STATS for '{}'".format(col_name))
    isna = df[col_name].isna().sum()
    print("NaNs: {:,} out of {:,} ({:.2f}%)".format(isna, len(df), 100.0*isna/len(df)))
    print("== Describe ==")
    print(df[col_name].describe())
    
    if n == -1:
        n = df[col_name].nunique()
        
    if not is_float_dtype(df[col_name]):
        print("== Value counts ==")
        print(df[col_name].value_counts()[:n])
        print("\n  Total unique values: {:,}\n".format(df[col_name].nunique()))
        
    print("== Head ==")
    print(df[col_name].head(n=7))
    
    
def column_hist(df, col_name):
    
    fig = px.histogram(df, x=col_name)
    fig.update_layout(
        title="Histogram of '{}'".format(col_name),
        xaxis_title=col_name,
        yaxis_title='Number of customers'
    )
    #fig.show()
    
    return fig
    
          
def columns_as_str(df, columns, uppercase=False, drop_empty=False, replace_na_value=''):
          
    """
    Convert columns to string, and convert to uppercase if specified.

    Note: This is done inplace.
    """
    
    if columns is None:
        columns = df.columns
        
    if isinstance(columns, str):
        columns = [columns]

    if not isinstance(columns, list):
        raise Exception("Expecting columns to be a list.")
    
    for c in columns:
        if c in df:
            if uppercase:    
                df.loc[:,c] = df[c].astype(str, skipna=True).str.upper()
            else:
                df.loc[:,c] = df[c].astype(str, skipna=True)

            if drop_empty:
                df.loc[:,c].replace(to_replace='', value=np.nan, inplace=True)
                df.dropna(subset=[c], inplace=True)
            else:
                df.loc[:,c].fillna(replace_na_value, inplace=True)

        else:
            print("Column '{}' doesn't exist.".format(c))

            
def columns_as_datetime(df, columns, datetime_format='%Y-%m-%d %H:%M:%S'):
    
    """
    Convert columns to time-zone-agnostic datetime.

    Note: This is done inplace.
    """
    
    if columns is None:
        columns = df.columns
        
    if isinstance(columns, str):
        columns = [columns]

    if not isinstance(columns, list):
        raise Exception("Expecting columns to be a list.")

    for c in columns:
        if c in df:
            df.loc[:,c] = pd.to_datetime(df[c], format=datetime_format, utc=True).dt.tz_convert(None)
        else:
            print("Column '{}' doesn't exist.".format(c))


def columns_as_float(df, columns, na_replace_value=None, drop_na=True):
    
    """
    Convert columns to float.

    Note: This is done inplace.
    """
    
    if columns is None:
        columns = df.columns
        
    if isinstance(columns, str):
        columns = [columns]
        
    if not isinstance(columns, list):
        raise Exception("Expecting columns to be a list.")

    if na_replace_value is None:
        na_replace_value = np.nan
    else:
        drop_na = False
        
    for c in columns:
        if c in df and not is_float_dtype(df[c]):
            
            if is_string_dtype(df[c]):
                df.loc[:,c].replace({
                    '' : np.nan, 'nan' : np.nan, 'NaN' : np.nan, 'None' : np.nan
                }, inplace=True)
                
            if drop_na:
                df.dropna(subset=[c], how='any', inplace=True)
            else:
                df.loc[:,c].fillna(na_replace_value, inplace=True)

            df.loc[:,c] = df[c].astype('float64', skipna=False)
        else:
            if is_float_dtype(df[c]):
                if drop_na:
                    df.dropna(subset=[c], how='any', inplace=True)
                else:
                    df.loc[:,c].fillna(na_replace_value, inplace=True)
                
            if c not in df:
                print("Column '{}' doesn't exist.".format(c))

        

def columns_as_int(df, columns, na_replace_value=None, drop_na=True):
    
    """
    Convert string/float columns to integer.

    Note: This is done inplace.
    """
    
    if columns is None:
        columns = df.columns
        
    if isinstance(columns, str):
        columns = [columns]
        
    if not isinstance(columns, list):
        raise Exception("Expecting columns to be a list.")
        
    if not drop_na and na_replace_value is None:
        na_replace_value = -1.0

    columns_as_float(df, columns, na_replace_value, drop_na)
    
    for c in columns:
        if c in df:
            df.loc[:,c] = df[c].astype('int64', skipna=False)
        else:
            print("Column '{}' doesn't exist.".format(c))
            
            
def agg_first(series, **kwargs):
    return series.iloc[0]

def agg_last(series, **kwargs):
    return series.iloc[-1]

def agg_nth(series, **kwargs):
    n = kwargs['n']
    if n >= len(series):
        return np.nan
    
    return series.iloc[n]

def agg_list(series, **kwargs):
    return "{}".format(list(series.to_numpy()))


def agg_sequence(series, **kwargs):
    
    d = kwargs['delimiter']
    s = d.join(item for item in series.to_numpy().astype(str))
    
    if kwargs['do_sorting']:
        return d.join(item for item in np.sort( list(set(s.split(d))) ))
    
    return d.join(item for item in list(set(s.split(d))))


def agg_umode(series):
    modes = series.mode()
    return modes.iloc[0]

    
def aggregate_columns(df, agg_type, agg_column, columns, copy_agg_column=False, **kwargs):
    
    """
    Aggregate values of columns, collapsing them.

    Note: This is not done inplace.
    """
    
    if agg_column not in df:
        print("[aggregate_columns] '{}' does not exist!!".format(agg_column))
        return None
    
    if len(columns) == 0:
        return None
    
    for c in columns:
        if c not in df:
            print("[aggregate_columns] '{}' does not exist!!".format(c))
    
    aggregators = {
        'mean' : pd.DataFrame.mean,
        'sum'  : pd.DataFrame.sum,
        'min'  : pd.DataFrame.min,
        'max'  : pd.DataFrame.max,
        'std'  : pd.DataFrame.std,
        'any'  : pd.DataFrame.any,
        'mode' : agg_umode,
        'first': agg_first,
        'last' : agg_last,
        'nth'  : agg_nth,
        'list' : agg_list,
        'seq'  : agg_sequence,
    }
    
    if agg_type in aggregators:
        func = aggregators[agg_type]
    else:
        raise NameError('[aggregate_columns] Need to add {} to transform function'.format(agg_type))
        
    cols = [c for c in columns if c in df]
    assert len(cols) > 0, f"[aggregate_columns] The columns [{columns}] to aggregate {agg_type} over is the empty array, which means we will aggregate over ALL columns. Do you mean to do this?"
    return df.groupby(by=agg_column)[cols].agg(func, **kwargs)




def transactions_cleanup(df, datetime_column, tid_column = 'Transaction_ID', cid_column = 'Customer_ID', datetime_format='%Y-%m-%d %H:%M:%S'):
    
    """
    Perform common transaction data cleanup.

    Note: This is done inplace.
    """
    
    df.loc[:,datetime_column] = pd.to_datetime( df[datetime_column], format=datetime_format)
    df.loc[:,datetime_column].dropna(inplace=True)

    # Get transactions date range
    print('Date range from {0} to {1}'.format(df[datetime_column].min(), df[datetime_column].max())) 
    
    # Remove column 'Unnamed: 0' if it exists
    if 'Unnamed: 0' in df:
        df.drop('Unnamed: 0', axis=1, inplace=True)
        print("Removed unnamed index column")

    print("Before dropping empty Transaction IDs: {:,}".format(len(df)))

    # Drop Transaction_ID's that are empty
    df.loc[:,tid_column].replace('', np.nan, inplace=True)
    df.dropna(subset=[tid_column], inplace=True)

    print("After: {:,}".format(len(df)))
    
    print("Before dropping empty Customer IDs: {:,}".format(len(df)))

    # Drop [cid]'s that are empty
    df.loc[:,cid_column].replace('', np.nan, inplace=True)
    df.dropna(subset=[cid_column], inplace=True)

    print("After: {:,}".format(len(df)))


def email_ensure_zero_or_one_activity_per_broadcast(
    df, cid_column = 'Customer_ID', activity_column = 'Activity', 
    activity_datetime_column = 'Activity_Datetime',
    verbose=True
):

    """
    Ensure each email sent to each customer has only one event: either a delivery, an open, a click, or a transaction,
    in that order. Keep only the first (in time) occurrence of it, in case of duplicate events.

    Note: This is done inplace.
    """
    
    conv_table = {
        'DELIVERY' : 0,
        'OPEN' : 1,
        'UNSUBSCRIBE' : 2,
        'CLICK' : 3,
        'TRANSACTION' : 4
    }
    
    if verbose:
        print("[email_ensure_zero_or_one_activity_per_broadcast] converting activities to ordinals...")
    
    df.loc[:,'activity_id'] = df[activity_column].apply(
        lambda x: conv_table.get(x,len(conv_table))
    )
 
    if verbose:
        print("[email_ensure_zero_or_one_activity_per_broadcast] get max...")

    result = df.groupby(by=[cid_column, 'Broadcast_ID'])['activity_id'].max()
    
    if verbose:
        print("[email_ensure_zero_or_one_activity_per_broadcast] determining which rows to keep...")
        
    df.loc[:,'keep'] = df.apply(lambda x: 1 if result[x[cid_column],x['Broadcast_ID']] == x['activity_id'] else 0, axis=1)

    if verbose:
        print("[email_ensure_zero_or_one_activity_per_broadcast] dropping...")
    df.drop(index=df[df.keep == 0].index, inplace=True)
    
    if verbose:
        print("[email_ensure_zero_or_one_activity_per_broadcast] sorting and keeping only the first occurence of the activity...")
        
    df.sort_values(by=[cid_column, 'Broadcast_ID', activity_datetime_column], inplace=True)
    df.drop_duplicates(subset=[cid_column, 'Broadcast_ID'], keep='first', inplace=True)

    del df['keep']
    del df['activity_id']



def email_keep_activities(df, activities):
    
    """
    Keep only certain email activities, remove the rest.

    Note: This is done inplace.
    """
    
    keep = df.Activity.isin(activities)
    df.drop(index=df[~keep].index, inplace=True)
    
    
def email_activity_stats(df, activity_column='Activity'):
    
    n = []
    n.append(len(df[df[activity_column] == 'DELIVERY']))
    n.append(len(df[df[activity_column] == 'OPEN']))
    n.append(len(df[df[activity_column] == 'CLICK']))
    n.append(len(df[df[activity_column] == 'TRANSACTION']))
    n.append(len(df[df[activity_column] == 'UNSUBSCRIBE']))
    n.append(len(df) - np.sum(n))
    N = np.sum(n)
    
    stats = {
        'Delivered' : n[0],
        'Delivered_perc' : 100.0 * n[0]/N,
        'Opens' : n[1],
        'Opens_perc' : 100.0 * n[1]/N,
        'Clicks' : n[2],
        'Clicks_perc' : 100.0 * n[2]/N,
        'Transactions' : n[3],
        'Transactions_perc' : 100.0 * n[3]/N,
        'Unsubscribes' : n[4],
        'Unsubscribes_perc' : 100.0 * n[4]/N,
        'Other' : n[5],
        'Other_perc' : 100.0 * n[5]/N,
        'Total' : np.sum(n)
    }

    return stats


def print_email_activity_stats(df, activity_column='Activity'):
    
    stats = email_activity_stats(df, activity_column=activity_column)
    
    print("Deliveries:   {:,} ({:.2f} %)".format(stats['Delivered'], stats['Delivered_perc']))
    print("Opens:        {:,} ({:.2f} %)".format(stats['Opens'], stats['Opens_perc']))
    print("Clicks:       {:,} ({:.2f} %)".format(stats['Clicks'], stats['Clicks_perc']))
    print("Transactions: {:,} ({:.2f} %)".format(stats['Transactions'], stats['Transactions_perc']))
    print("Unsubscribes: {:,} ({:.2f} %)".format(stats['Unsubscribes'], stats['Unsubscribes_perc']))
    print("Other:        {:,} ({:.2f} %)".format(stats['Other'], stats['Other_perc']))
    print("Total:        {:,}".format(stats['Total']))
    
    
def transaction_stats(
    df,
    cid_column='Customer_ID',
    datetime_column='Datetime',
    max_bins=100
):
    
    df.loc[:,'rank'] = df.sort_values(by=[cid_column, datetime_column]). \
        groupby(by=[cid_column])[datetime_column].rank(method='dense')
    #df.loc[:,'trans'] = 1
    
    n_trans = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])['rank'].max()
    #n_trans = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])['trans'].sum()

    df_n_trans = pd.DataFrame()
    df_n_trans.loc[:,cid_column] = n_trans.index
    df_n_trans.loc[:,'n_trans'] = n_trans.to_numpy()

    hist_n_trans = df_n_trans['n_trans'].value_counts()

    df_trans_hist = pd.DataFrame()
    df_trans_hist['n_trans'] = hist_n_trans.index
    df_trans_hist['count'] = hist_n_trans.values
    df_trans_hist.sort_values(by=['n_trans'], inplace=True)
    print(df_trans_hist.head(max_bins))
    
    fig = column_hist(df_n_trans, 'n_trans')
    
    del df['rank']
    
    print("Period {} to {}".format(df[datetime_column].min(), df[datetime_column].max()))
    print("Total sales: {:,} ({:,} customers)".format(len(df), df[cid_column].nunique()))
    print("Order segment 3+: {:,} customers".format(df_trans_hist[df_trans_hist['n_trans'] > 2]['count'].sum()))
    
    return fig, df_trans_hist


def keep_subset_customers(dataframes, cid_column, k, seed=1):
    """
    Keep a subset of customers among all dataframes.
    
    Input:
    dataframes - Either a single dataframe or a list of dataframes.
    
    Is not done inplace.
    """
    import random
    
    random.seed(seed)
    
    dataframes_in = dataframes
    if isinstance(dataframes, list):
        df = dataframes[0]
    else:
        df = dataframes
        dataframes_in = [dataframes]
    
    print("{:,} unique customers".format(df[cid_column].nunique()))
    
    cids = list(df[cid_column].unique())
    to_keep_cids = random.sample(cids, k=k)
    to_keep_cids_map = {cid:1 for cid in to_keep_cids}

    dataframes_out = []
    for df in dataframes_in:
        df.loc[:,'keep'] = df[cid_column].apply(lambda x: to_keep_cids_map.get(x,0))
        dataframes_out.append( df.drop(index=df[df.keep == 0].index))
    
    print("{:,} unique customers after sampling".format(dataframes_out[0][cid_column].nunique()))
    
    if isinstance(dataframes, list):
        return dataframes_out
    
    return dataframes_out[0]


def filter_dataframe(df, match_filters=None, contains_filters=None):
    #
    # Perform any filtering
    #
    if match_filters is not None:
        for c,v in match_filters.items():
            if c in df:
                filter_vals = '|'.join(v)

                column_stats(df, c)
                print(f"Before 'match' filtering column '{c}' -> '{filter_vals}': n={len(df)}")
                df = df.loc[df[c].str.match(filter_vals),:].copy()
                print(f"After 'match' filtering column '{c}' -> '{filter_vals}': n={len(df)}")
                column_stats(df, c)
                
    if contains_filters is not None:
        for c,v in contains_filters.items():
            if c in df:
                filter_vals = '|'.join(v)

                column_stats(df, c)
                print(f"Before 'contains' filtering column '{c}' -> '{filter_vals}': n={len(df)}")
                df = df.loc[df[c].str.contains(filter_vals),:].copy()
                print(f"After 'contains' filtering column '{c}' -> '{filter_vals}': n={len(df)}")
                column_stats(df, c)

    return df


def mann_whitney_test(dfA, dfB, column, group_A_name='grp_A', group_B_name='grp_B', scale = 1.0, unit='', verbose=False):
    
    from scipy.stats import mannwhitneyu as mw
    
    try:
        dfa = dfA[~dfA[column].isnull()]
        dfb = dfB[~dfB[column].isnull()]
        
        p = mw(dfa[column], dfb[column])[1]
        
        na = len(dfa)
        nb = len(dfb)
        
        if verbose:
            print('{}: sum/mean (scale={})/median (scale={}) \n A={:,}/{:.3f}{}/{:.3f}{} (n={:,}), B={:,}/{:.3f}{}/{:.3f}{} (n={:,}), p={:.3f}'.format(
                column, scale, scale,
                int(dfa[column].sum()),
                dfa[column].mean() * scale,
                unit,
                dfa[column].median() * scale,
                unit,
                na, 
                int(dfb[column].sum()),
                dfb[column].mean() * scale, 
                unit,
                dfb[column].median() * scale,
                unit,
                nb, 
                p
            ))
        
        data = []
        data.append((
            column,
            
            #int(dfa[column].sum()),
            dfa[column].mean() * scale,
            dfa[column].median() * scale,
            na,
            
            #int(dfb[column].sum()),
            dfb[column].mean() * scale,
            dfb[column].median() * scale,
            nb,
            
            p
        ))
        
        #df_out = pd.DataFrame(data, columns=[
        #    f'driver',
        #    #f'sum_{group_A_name}',
        #    f'mean_{group_A_name}',
        #    f'median_{group_A_name}',
        #    f'size_{group_A_name}',
        #    
        #    #f'sum_{group_B_name}',
        #    f'mean_{group_B_name}',
        #    f'median_{group_B_name}',
        #    f'size_{group_B_name}',
        #    
        #    f'mann_whitney_p_value',
        #])
        df_out = pd.DataFrame(data, columns=[
            'column',
            #f'sum_{group_A_name}',
            '{}_mean'.format(group_A_name),
            '{}_median'.format(group_A_name),
            '{}_size'.format(group_A_name),
            
            #f'sum_{group_B_name}',
            '{}_mean'.format(group_B_name),
            '{}_median'.format(group_B_name),
            '{}_size'.format(group_B_name),
            
            'mann_whitney_p_value',
        ])
        
        #print(df_out.head())
        
        return df_out, p
            
    except:
        
        return None, np.nan
    
    return None, np.nan


def parallelise_dataframe(df, func, on_cids=False, n_cores=2):
    if on_cids:
        print("[parallelise_data_frame_on_cids] Assigning Customer_IDs to cores...")
        cid2batch = {cid:(i % n_cores) for i,cid in enumerate(df.Customer_ID.unique())}
        df.loc[:,'core'] = df.Customer_ID.apply(lambda cid: cid2batch.get(cid, 0))
        df_split = [df[df.core == i] for i in range(n_cores)]
    else:
        df_split = np.array_split(df, n_cores)

    print(f"Executing on {n_cores} cores...")
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))

    pool.close()
    pool.join()

    return df
