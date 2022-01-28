# -*- coding: utf-8 -*-
""" transformers.py

A collection of often-used sklearn custom Transformers.

"""

import pandas as pd
import numpy as np
import inspect, sys
import datetime

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import FeatureUnion, _fit_transform_one, _transform_one
from joblib import Parallel, delayed

from scipy import sparse

import humailib.utils as hu


def get_all_transformers():
    for name, obj in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(obj):
            print(obj)


class DataframeFunctionTransformer(BaseEstimator, TransformerMixin):
    """
    Transform dataframe with a custom function.
    The function, func, needs to be of the format:
      func(X, params)
    """
    def __init__(self, func, params):
        self.func = func
        self.params = params

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None, copy=None):
        
        #assert isinstance(input_df, pd.DataFrame) or isinstance(input_df, pd.Series)
        
        print("[DataframeFunctionTransformer] with function '{}' on {:,} rows...".format(self.func.__name__, len(X)))
        print("  params={}".format(self.params))
        return self.func(X, self.params)
    
    
class DataframeFeatureUnion(FeatureUnion):
    """
    FeatureUnion that works and preserves pandas Dataframes.
    From: https://zablo.net/blog/post/pandas-dataframe-in-scikit-learn-feature-union/
    
    If using PipelineBuilder, treat a DataframeFeatureUnion as a transformer step in the
    pipeline.
    
    Example:
    
        pipeline_builder = PipelineBuilder()
        pipeline_builder.new_pipeline('aggregate_and_finalise')        
        ...
        
        df_aggregate = pipeline_builder.transform_and_add([
            ('aggregate_customers', ht.DataframeFeatureUnion([
                ('agg_max', ht.Aggregator(
                    agg_type='max', agg_column='Customer_ID', columns=['A','B'],
                    copy_agg_column=True
                )), 
                ('agg_mean', ht.Aggregator(
                    agg_type='mean', agg_column='Customer_ID', columns=['C','D'],
                    copy_agg_column=False
                )),
                ('agg_sum', ht.Aggregator(
                    agg_type='sum', agg_column='Customer_ID', columns=['E','F'],
                    copy_agg_column=False
                )) 
            ], n_jobs=3)
            )
        ], df)

    """
    
    def fit_transform(self, X, y=None, **fit_params):
        self._validate_transformers()
        result = Parallel(n_jobs=self.n_jobs)(
            delayed(_fit_transform_one)(trans, weight=weight, X=X, y=y,
                                        **fit_params)
            for name, trans, weight in self._iter()
        )

        if not result:
            # All transformers are None
            return np.zeros((X.shape[0], 0))
        
        Xs, transformers = zip(*result)
        self._update_transformer_list(transformers)
        if any(sparse.issparse(f) for f in Xs):
            Xs = sparse.hstack(Xs).tocsr()
        else:
            Xs = self.merge_dataframes_by_column(Xs)
            
        return Xs

    def merge_dataframes_by_column(self, Xs):
        return pd.concat(Xs, axis="columns", copy=False)

    def transform(self, X):
        Xs = Parallel(n_jobs=self.n_jobs)(
            delayed(_transform_one)(trans, weight=weight, X=X, y=None)
            for name, trans, weight in self._iter()
        )
        
        if not Xs:
            # All transformers are None
            return np.zeros((X.shape[0], 0))
        
        if any(sparse.issparse(f) for f in Xs):
            Xs = sparse.hstack(Xs).tocsr()
        else:
            Xs = self.merge_dataframes_by_column(Xs)
            
        return Xs
    

class CrossReferenceTransformer(BaseEstimator, TransformerMixin):
    """
    Cross reference a column in X with the same column in a reference
    dataframe, and return the values from the return column.
    
    Parameters
    ----------
    df_ref : The reference data frame that contains the reference column
             as well as the return column
    ref_column : The reference column that is present in both the dataframe
                 as well as the reference frame
    ret_column : Which column to return from the reference frame
    na_value : Any missing values will be replaced with this value
    """
    def __init__(self, df_ref, ref_column, ret_column, na_value=np.nan):
        self.df_ref = df_ref
        self.ref_column = ref_column
        self.ret_column = ret_column
        self.na_value = na_value
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[CrossReferenceTransformer] transform on {:,}...".format(len(X)))
        print("  Cross-referencing {}, and returning {}".format(self.ref_column, self.ret_column))
        
        a_to_b = {a:b for a,b in zip(self.df_ref[self.ref_column].to_numpy(), self.df_ref[self.ret_column].to_numpy())}
    
        df = X.copy()
        df.loc[:,self.ret_column] = X.apply(
            lambda x: a_to_b.get(x[self.ref_column], self.na_value), 
            axis=1
        )
        
        return df
    

class KeepMostRecentTransformer(BaseEstimator, TransformerMixin):
    """
    Keep the most recent n rows for each entity of [agg_column]
    """
    def __init__(self, agg_column, datetime_column, columns=None, n=5):
        self.agg_column = agg_column
        self.datetime_column = datetime_column
        self.columns = columns
        self.n = n
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[KeepMostRecentTransformer] transform on {:,}...".format(len(X)))
        print("  agg_column={}, columns={}, n={}".format(self.agg_column, self.columns, self.n))
        
        df = X.copy()

        df.loc[:,'kmr_ranking'] = df.sort_values(
            by=[self.agg_column, self.datetime_column]
        ).groupby(by=self.agg_column)[self.datetime_column].rank(method='first', ascending=False)

        df = df[df['kmr_ranking'] <= self.n]
        
        print("[KeepMostRecentTransformer] left {:,} rows, or {:,} {}s.".format(len(df), df[self.agg_column].nunique(), self.agg_column))

        if self.columns:
            df = df[self.columns]
        else:
            del df['kmr_ranking']

        return df
    
    
class ColumnStatsTransformer(BaseEstimator, TransformerMixin):
    """
    Print out exploratory information for certain columns in a dataframe. 
    """
    def __init__(self, columns=None, max_rows=5):
        self.columns = columns
        self.max_rows = max_rows
        
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[ColumnStatsTransformer] stats {}...".format(self.columns))
        
        if self.columns is not None:
            for c in self.columns:
                hu.column_stats(X, c, n=self.max_rows)
            
        return X 
           
        
class SelectColumnsTransformer(BaseEstimator, TransformerMixin):
    """
    Select which columns to keep, and discard the rest.
    """
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[SelectColumnsTransformer] select {}...".format(self.columns))
        cpy_df = X[self.columns].copy()
        return cpy_df


class DropColumnsTransformer(BaseEstimator, TransformerMixin):
    """
    Drop certain columns from a dataframe.
    """
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[DropColumnsTransformer] drop {}...".format(self.columns))
        
        return X.drop(columns=self.columns)
    
    
class DropDuplicatesTransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, subset=None):
        self.subset = subset

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[DropDuplicatesTransformer] dropping duplicates of {} on {:,}...".format(self.subset, len(X)))
    
        df = X.drop_duplicates(subset=self.subset)
    
        print("[DropDuplicatesTransformer] left: {:,}".format(len(df)))
    
        return df
    
    
class DropNATransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, subset=None):
        self.subset = subset

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[DropNATransformer] dropping NaNs of {} on {:,}...".format(self.subset, len(X)))
    
        df = X.dropna(subset=self.subset)
    
        print("[DropNATransformer] left: {:,}".format(len(df)))
    
        return df  
    
    
class DropEmptyStringTransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, column=None):
        self.column = column

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[DropEmptyStringTransformer] dropping empty strings of {} on {:,}...".format(self.column, len(X)))
    
        df = X.copy()
        
        df.drop(index=df[df[self.column].str.strip() ==''].index, inplace=True)
    
        print("[DropEmptyStringTransformer] left: {:,}".format(len(df)))
    
        return df  
    
    
class SortingTransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, columns=None):
        self.columns = columns

    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[SortingTransformer] sorting on {} on {:,}...".format(self.columns, len(X)))
    
        df = X.sort_values(by=self.columns).copy()
    
        return df
    
    
class IntTypeTransformer(BaseEstimator, TransformerMixin):
    
    """
    """ 
    def __init__(self, columns = None, na_replace_value=None, drop_na=False):
        self.columns = columns
        self.na_replace_value = na_replace_value
        self.drop_na = drop_na
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[IntTypeTransformer] transforming {} on {:,}...".format(self.columns, len(X)))
        print("  na_replace_value={}, drop_na={}".format(self.na_replace_value, self.drop_na))

        df = X.copy()
        hu.columns_as_int(df, columns=self.columns, na_replace_value=self.na_replace_value, drop_na=self.drop_na)

        print("[IntTypeTransformer] left: {:,}".format(len(df)))

        return df

    
class StrTypeTransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, columns = None, uppercase=False, drop_empty=False):
        self.columns = columns
        self.uppercase = uppercase
        self.drop_empty = drop_empty
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[StrTypeTransformer] transform {} on {:,}...".format(self.columns, len(X)))
        print("  uppercase={}, drop_empty={}".format(self.uppercase, self.drop_empty))

        df = X.copy()
        hu.columns_as_str(
            df, columns=self.columns, uppercase=self.uppercase, drop_empty=self.drop_empty
        )
        
        if self.drop_empty:
            print("[StrTypeTransformer] after dropping '': {:,}".format(len(df)))
        
        return df

    
class DatetimeTypeTransformer(BaseEstimator, TransformerMixin):
    """
    """
    def __init__(self, columns = None, datetime_format='%Y-%m-%d %H:%M:%S'):
        self.columns = columns
        self.datetimeformat = datetimeformat
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[DatetimeTypeTransformer] transform {} on {:,}...".format(self.columns, len(X)))
        print("  datetimeformat={}".format(self.datetimeformat))

        df = X.copy()
        hu.columns_as_datetime(df, columns=self.columns, datetime_format=self.datetimeformat)
        
        return df
    
"""
"""    
class TransactionsCleanupTransformer(BaseEstimator, TransformerMixin):
    
    def __init__(self, datetime_column = 'Datetime', tid_column = 'Transaction_ID', cid_column = 'Customer_ID', datetime_format='%Y-%m-%d %H:%M:%S'):
        self.datetime_column = datetime_column
        self.tid_column = tid_column
        self.cid_column = cid_column
        self.datetime_format = datetime_format
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[TransactionsCleanupTransformer] transform on {:,}...".format(len(X)))
        
        print("  datetime_column={}, tid_column={}, cid_column={}".format(
            self.datetime_column, self.tid_column, self.cid_column
        ))

        df = X.copy()
        hu.transactions_cleanup(
            df, 
            datetime_column = self.datetime_column, 
            tid_column = self.tid_column, 
            cid_column = self.cid_column, 
            datetime_format=self.datetime_format
        )
        
        return df
    
    
class KeepEmailActivitiesTransformer(BaseEstimator, TransformerMixin):
    """
    """
    
    def __init__(self, activities):
        self.activities = activities
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[KeepEmailActivitiesTransformer] keeping {} on {:,}...".format(self.activities, len(X)))

        df = X.copy()
        hu.email_keep_activities(
            df,
            activities=self.activities
        )
        
        print("[KeepEmailActivitiesTransformer] left {:,}".format(len(df)))
        
        return df
    

class UniqueEmailEventsTransformer(BaseEstimator, TransformerMixin):
    """
    """
    
    def __init__(self, cid_column = 'Customer_ID', activity_column = 'Activity', activity_datetime_column = 'Activity_Datetime', verbose=True):
        self.cid_column = cid_column
        self.activity_column = activity_column
        self.activity_datetime_column = activity_datetime_column
        self.verbose = verbose
        return
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[UniqueEmailEventsTransformer] transform on {:,}...".format(len(X)))
        print("  cid_column={}, activity_column={}, activity_datetime_column={}".format(
            self.cid_column, self.activity_column, self.activity_datetime_column
        ))

        df = X.copy()
        hu.email_ensure_zero_or_one_activity_per_broadcast(
            df, 
            cid_column = self.cid_column,
            activity_column = self.activity_column,
            activity_datetime_column = self.activity_datetime_column,
            verbose=self.verbose
        )
        
        print("[UniqueEmailEventsTransformer] left {:,}".format(len(df)))
        
        return df
    
    
    
class SeasonalityTransformer(BaseEstimator, TransformerMixin):
    
    """
    Calculate seasonality labels (one-hot encoding type) for each row
    
    Input dataframes could be:
        1. Items (to get product seasonality)
        2. Transactions (to get customer seasonality)
    """
    
    def __init__(self, datetime_column = 'Datetime'):
        self.datetime_column = datetime_column
        #print(self.datetime_column)
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[SeasonalityTransformer] transform on {:,}...".format(len(X)))
        
        df = X.copy()
        #print(df.head())
    
        print("  spring...")
        df.loc[:,'spring'] = df.apply(
            lambda x: 1.0 if (4 <= x[self.datetime_column].month < 7) else 0.0, axis=1
        )

        print("  summer...")
        df.loc[:,'summer'] = df.apply(
            lambda x: 1.0 if (7 <= x[self.datetime_column].month < 10) else 0.0, axis=1
        )

        print("  autumn...")
        df.loc[:,'autumn'] = df.apply(
            lambda x: 1.0 if (10 <= x[self.datetime_column].month <= 12) else 0.0, axis=1
        )

        print("  winter...")
        df.loc[:,'winter'] = df.apply(
            lambda x: 1.0 if (1 <= x[self.datetime_column].month < 4) else 0.0, axis=1
        )
        
        print("[SeasonalityTransformer] Done.")

        return df
    

class TimeOfDayTransformer(BaseEstimator, TransformerMixin):
    
    """
    Calculate email activity time-of-day (one-hot encoding type) for each row
    
    Input dataframe:
      1. Email events
    """
    
    def __init__(self, datetime_column = 'Datetime'):
        self.datetime_column = datetime_column
        #print(self.datetime_column)
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[TimeOfDayTransformer] transform on {:,}...".format(len(X)))
        
        df = X.copy()
        #print(df.head())
    
        print("  morning...")
        df.loc[:,'morning'] = df.apply(
            lambda x: 1.0 if (0 <= x[self.datetime_column].hour < 12) else 0.0, axis=1
        )

        print("  daytime...")
        df.loc[:,'daytime'] = df.apply(
            lambda x: 1.0 if (12 <= x[self.datetime_column].hour < 17) else 0.0, axis=1
        )

        print("  evening...")
        df.loc[:,'evening'] = df.apply(
            lambda x: 1.0 if (17 <= x[self.datetime_column].hour <= 23) else 0.0, axis=1
        )
        
        print("[TimeOfDayTransformer] Done.")

        return df



class GenderTransformer(BaseEstimator, TransformerMixin):
    
    """
    Calculate gender labels (one-hot encoding type) for each row
    
    Input dataframes could be:
        1. Items (to get product 'gender', i.e. what proportion of the product is bought by male, female, unisex)
    """
    
    def __init__(self, df_trans, df_customers, cid_column = 'Customer_ID', gender_column = 'Gender'):
        self.cid_to_gender = {cid:gender for cid,gender in zip(df_customers[cid_column].values, df_customers[gender_column].values) }
        self.tid_to_gender = {tid:self.cid_to_gender[cid] for tid,cid in zip(df_trans['Transaction_ID'].values, df_trans[cid_column].values)}
        self.cid_column = cid_column
        #print(self.datetime_column)
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[ProductGenderTransformer] transform on {:,}...".format(len(X)))
        
        df = X.copy()
        
        df.loc[:,'male'] = df['Transaction_ID'].apply(
            lambda x: 1.0 if (x in self.tid_to_gender and self.tid_to_gender[x] == 'M') else 0.0, 
                                   axis=1
        )
        df.loc[:,'female'] = df['Transaction_ID'].apply(
            lambda x: 1.0 if (x in self.tid_to_gender and self.tid_to_gender[x] == 'F') else 0.0, 
                                   axis=1
        )
        df.loc[:,'unisex'] = df['Transaction_ID'].apply(
            lambda x: 1.0 if (x in self.tid_to_gender and (self.tid_to_gender[x] != 'M' and self.tid_to_gender[x] != 'F')) else 0.0, 
                                   axis=1
        )        

        return df

    
class Aggregator(BaseEstimator, TransformerMixin):
    """
    """ 
    def __init__(self, agg_type, agg_column, columns, **kwargs):
        self.agg_type = agg_type
        self.agg_column = agg_column
        self.columns = columns
        self.kwargs = kwargs
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        assert self.agg_column in X, "{} does not exist!!".format(self.agg_column)
        
        n = X[self.agg_column].nunique()
        print("[Aggregator] transform on {:,}...".format(n))
        print("  method='{}', agg_column='{}', columns={}".format(
            self.agg_type, self.agg_column, self.columns
        ))
        for c in self.columns:
            if c not in self.columns:
                print("[Aggregator] '{}' does not exist!!".format(c))
        
        df = hu.aggregate_columns(
            X.copy(),
            self.agg_type, 
            self.agg_column,
            self.columns,
            **self.kwargs
        )
        
        print("[Aggregator] Done.")
        
        return df
    
    
class AggregatorMean(Aggregator):
    """
    """ 
    def __init__(self, agg_column, columns, copy_agg_column=True):
        super.__init__('mean', agg_column, columns, copy_agg_column)
        return
    
        
class OrderSegmentTransformer(BaseEstimator, TransformerMixin):
    """
    """        
    
    def __init__(self, num_trans_column = 'n_trans', num_segments=3):
        self.num_trans_column = num_trans_column
        self.num_segments = num_segments
        return
    
    def fit(self, X, y=None):
        return
    
    def _get_segment(self, x):
        if x.n_trans >= self.num_segments:
            return 'os_{}+'.format(self.num_segments)
        
        return 'os_{}'.format(x.n_trans)

    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[OrderSegmentTransformer] transform on {:,}...".format(len(X)))

        df = X.copy()
        
        df.loc[:,'order_segment'] = df.apply(lambda x: self._get_segment(x), axis=1)
        
        return df
    
    
