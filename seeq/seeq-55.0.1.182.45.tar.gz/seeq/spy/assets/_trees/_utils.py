import re

import numpy as np
import pandas as pd


def set_name(df, new_name):
    df = df.copy()
    old_name = df.loc[0, 'Name']

    df.loc[0, 'Name'] = new_name
    pattern = re.compile(r'^' + re.escape(old_name) + r'(?=\s*>>|$)', flags=re.IGNORECASE)
    df['Path'] = df['Path'].str.replace(pattern, new_name)
    df['ID'] = np.nan

    return df


def upsert(df1, df2, prefer_right=True):
    """
    Upserts the data from df2 into df1 based on case-insensitive Path and Name values.
    If a row from df2 matches a row in df1, and the two have conflicting values, then preference
    is given as per the prefer_right parameter. Keeps the columns of df1
    """
    if len(df2) == 0:
        return df1
    if len(df1) == 0:
        return df2

    orig_columns = df1.columns
    df1 = df1.copy()
    df2 = df2.copy()
    for df in (df1, df2):
        df['path_nocase'] = df.Path.astype('object').str.casefold()
        df['name_nocase'] = df.Name.astype('object').str.casefold()
    df = df1.merge(df2, how='outer', on=['path_nocase', 'name_nocase'])
    wipe_ids = pd.Series(False, index=df.index)
    for column in orig_columns:
        prefer_right_column = prefer_right and column not in ['Path', 'Name']
        left_column = column + '_x'
        right_column = column + '_y'
        if right_column in df.columns:
            prefer_column = right_column if prefer_right_column else left_column
            backup_column = left_column if prefer_right_column else right_column
            df[column] = df[prefer_column]
            missing_values = pd.isnull(df[column])
            df.loc[missing_values, column] = df.loc[missing_values, backup_column]
            df[column] = df[column].apply(safe_int_cast)
            if column == 'Type' and 'ID' in df.columns:
                wipe_ids = wipe_ids | df.apply(lambda row: type_differs(row[prefer_column], row[backup_column]),
                                               axis=1)
    df.drop(columns=df.columns.difference(orig_columns), inplace=True)
    if 'ID' in df.columns:
        df.loc[wipe_ids, 'ID'] = np.nan
    return df


def drop_duplicate_items(df):
    """
    Removes duplicate items (identified by case-insensitive Path and Name) from a dataframe.
    """
    if len(df) == 0:
        return
    df['path_nocase'] = df.Path.astype('object').str.casefold()
    df['name_nocase'] = df.Name.astype('object').str.casefold()
    df.drop_duplicates(subset=['path_nocase', 'name_nocase'], inplace=True, ignore_index=True)
    df.drop(columns=['path_nocase', 'name_nocase'], inplace=True)


def safe_int_cast(x):
    return int(x) if isinstance(x, float) and not np.isnan(x) and x == int(x) else x


def initialize_status_df(status, action, *args):
    status.df = pd.DataFrame([{
        f'Assets {action}': 0,
        f'Signals {action}': 0,
        f'Conditions {action}': 0,
        f'Scalars {action}': 0,
        f'Total Items {action}': 0,
        f'Items Pulled From Seeq': 0,
        f'Errors Encountered': 0
    }], index=['Status'])
    status.update(*args)


def increment_status_df(status, new_items=None, pulled_items=None, error_items=None, subtract_errors=False):
    if new_items is not None:
        for column in status.df.columns:
            if 'Type' in new_items.columns:
                for item_type in ['Asset', 'Signal', 'Condition', 'Scalar']:
                    if item_type in column:
                        status.df[column] += sum(new_items['Type'].fillna('').str.contains(item_type))
            if 'Total' in column:
                status.df[column] += len(new_items)
    if pulled_items is not None:
        status.df['Items Pulled From Seeq'] += len(pulled_items)
    if error_items is not None:
        if subtract_errors:
            for column in status.df.columns:
                if 'Type' in error_items.columns:
                    for item_type in ['Asset', 'Signal', 'Condition', 'Scalar']:
                        if item_type in column:
                            status.df[column] -= sum(error_items['Type'].fillna('').str.contains(item_type))
                if 'Total' in column:
                    status.df[column] -= len(error_items)
        status.df['Errors Encountered'] += len(error_items)
    status.update()


def type_differs(t1, t2):
    if pd.isnull(t1) or pd.isnull(t2) or len(t1) == 0 or len(t2) == 0:
        return False
    if 'Calculated' in t1 and 'Stored' in t2:
        return False
    if 'Stored' in t1 and 'Calculated' in t2:
        return False
    for simple_type in ('Asset', 'Scalar', 'Signal', 'Condition'):
        if simple_type in t1 and simple_type in t2:
            return False
    return True
