import numpy as np
import pandas as pd
import datetime

from random import randrange
from datetime import timedelta

def get_training_features_for_small_data_transactions(
    df_trans,
    chars_transform_pipeline,
    df_trans_chars=None,
    cid_column='Customer_ID',
    datetime_column='Datetime'
):
    
    """
    Return labeled training data for small dataset where most customers place only one
    order.
    
    Training data built as follows:
      observed=0:
        People in order segment 1
        People in order segment 2 and up
      observed=1:
        People in order segment 2 and up, but with their last order removed (treated 
          as being the observed order), turning them into order segment 1 and up.
    
    Parameters
    ----------
    df_trans : Transactions table
    df_trans_chars : Customer transaction characteristics table calculated from the above.
    chars_transform_pipeline : Customer transaction characteristics pipeline used to get
        df_trans_chars
    cid_column : Name of Customer ID column
    datetime_column : Name of transaction datetime column
    
    Returns
    -------
    A dataframe with labeled ('observed' column) training data.
    """
    
    if df_trans_chars is None:
        df_trans_chars = chars_transform_pipeline.transform(df_trans)

    df = df_trans.copy()
    df.loc[:,'rank'] = df.sort_values(by=[cid_column, datetime_column]). \
        groupby(by=cid_column)[datetime_column].rank(method='min', ascending=False)

    # For each customer, remove their most recent transaction. This will 
    # remove all order-segment 1 customers, so we need to add these back in later.
    # Order segment 2 customers become order segment 1, and these are the customers
    # that we are most interested in comparing against the actual order segment 1; those
    # that did not do a repeat purchase.
    df_trans_os2_and_up_minus_last = df[df['rank'] > 1.0].sort_values(
        by=[cid_column, datetime_column]
    ).copy()    

    print("[get_training_features_for_small_data_transactions] Get characteristics for OS2 and up minus last")
    df_chars_os2_and_up_minus_last = chars_transform_pipeline.transform(df_trans_os2_and_up_minus_last)

    df_chars_os1 = df_trans_chars[df_trans_chars.n_trans == 1].copy()
    df_trans_os2_and_up = df_trans_chars[df_trans_chars.n_trans > 1].copy()

    a = set(df_chars_os1[cid_column].to_numpy())
    b = set(df_chars_os2_and_up_minus_last[cid_column].to_numpy())
    assert len( a & b ) == 0, "{:,} customers are in both order segment 1 as well as 2+.".format(len(a&b))

    df_chars_os1.loc[:,'observed'] = 0
    df_trans_os2_and_up.loc[:,'observed'] = 0
    df_chars_os2_and_up_minus_last.loc[:,'observed'] = 1

    full_to_dur = {a:b for a,b in zip(
        df_trans_chars[cid_column].to_numpy(),
        df_trans_chars['days_between_most_recent_trans'].to_numpy()
    ) }

    df_chars_os2_and_up_minus_last.loc[:,'last_trans_dur_days'] = df_chars_os2_and_up_minus_last[cid_column].apply(
        lambda x: full_to_dur.get(x, 0.0)
    )
    
    def random_within_timeframe(start, end):

        delta = end - start
        if delta.days == 0:
            return timedelta(seconds=0)

        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        return timedelta(seconds=randrange(int_delta))

    max_date = df[datetime_column].max()
    df_chars_os1.loc[:,'last_trans_dur_days'] = df_chars_os1.apply(
        lambda x: random_within_timeframe(x['last_trans_date'], max_date), axis=1)
    df_chars_os1.loc[:,'last_trans_dur_days'] = df_chars_os1['last_trans_dur_days'] / pd.to_timedelta(1, unit='D')
    df_trans_os2_and_up.loc[:,'last_trans_dur_days'] = df_trans_os2_and_up.apply(
        lambda x: random_within_timeframe(x['last_trans_date'], max_date), axis=1)
    df_trans_os2_and_up.loc[:,'last_trans_dur_days'] = df_trans_os2_and_up['last_trans_dur_days'] / pd.to_timedelta(1, unit='D')
        
    df_training_chars = df_chars_os1.append([df_chars_os2_and_up_minus_last, df_trans_os2_and_up], sort=True)
    
    return df_training_chars


def get_training_basic_features_transactions(df, date_column, cid, max_hist_len, min_timespan_wks=3, min_unique_wks = 2, make_weeks_whole = True, verbose=False):
    
    df.loc[:,'week_of_year'] = df.loc[:,date_column].apply(lambda x: x.weekofyear)

    dfg_customers = df.sort_values(by=[cid, date_column]).groupby(by=[cid])
    nc = len(dfg_customers)
    print("Number of customers: {:,}".format(nc))
    
    features = []

    ii = 0

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        timespan_wks = int((g.iloc[-1,:][date_column] - g.iloc[0,:][date_column]).days / 7) + 1
        if timespan_wks >= min_timespan_wks:
            #print(cid)
            #print(g)
            cutoff_wks = np.random.randint(0, max(0, min(max_hist_len-1, timespan_wks-1))) if timespan_wks > 1 else 0
            
            start_date = g.iloc[0,:][date_column]
            end_date = start_date + datetime.timedelta(weeks=cutoff_wks)
            #print("Start: {}, end {}".format(start_date, end_date))
            timespan_wks = int((end_date - g.iloc[0,:][date_column]).days / 7) + 1
            
            transactions = g[ (g[date_column] >= start_date) & (g[date_column] <= end_date) ].copy()
            if transactions['week_of_year'].nunique() >= min_unique_wks:
                #print(g)

                observed = 1 if g.iloc[-1,:][date_column] == transactions.iloc[-1,:][date_column] else 0
                n_trans = len(transactions) - observed

                transactions.drop_duplicates(subset=['week_of_year'], keep='last', inplace=True)
                act_wks = len(transactions) - observed

                if observed:
                    last_trans_dur_wks = int((transactions.iloc[-1,:][date_column] - transactions.iloc[-2,:][date_column]).days / 7) + 1
                    timespan_wks = int((transactions.iloc[-2,:][date_column] - transactions.iloc[0,:][date_column]).days / 7) + 1
                else:
                    last_trans_dur_wks = int((end_date - transactions.iloc[-1,:][date_column]).days / 7) + 1
                    timespan_wks = int((transactions.iloc[-2,:][date_column] - transactions.iloc[0,:][date_column]).days / 7) + 1

                nonact_wks = max(0, timespan_wks - act_wks)
                #print("start_week {}, end_week {}".format(start_week, end_week))
                #print("observed {}, last_trans_dur {}, n_trans {}, act_wks {}, nonact_wks {}, timespan_wks {}".format(observed, last_trans_dur, n_trans, act_wks, nonact_wks, timespan_wks))

                features.append((cid, observed, transactions.iloc[-2,:][date_column], last_trans_dur_wks, n_trans, act_wks, nonact_wks, timespan_wks))
        
        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(
        features, columns=[
            'cid', 'observed', 'last_transaction_date', 'last_trans_dur_wks', 'n_trans', 'act_wks', 'nonact_wks', 'timespan_wks'
        ])

    return df_features

def get_prediction_basic_features_transactions(df, timepoint, max_hist_len = 12,
                                           date_column = 'Datetime', cid_column = 'Customer_ID', 
                                           verbose=False):
    
    df.loc[:,'week_of_year'] = df[date_column].apply(lambda x: x.weekofyear)

    dfg_customers = df.sort_values(by=[cid_column, date_column]).groupby(by=[cid_column])
    nc = len(dfg_customers)
    print("Number of customers: {:,}".format(nc))
    print("Transaction stats: {}".format(dfg_customers['Transaction_ID'].count().describe()))
    
    features = []

    ii = 0

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        if len(g) >= 1:
            #print("cid {}".format(cid))
            #print("g (n={}) {}".format(len(g),g))
            
            end_date = g.iloc[-1,:][date_column]
            start_date = end_date - datetime.timedelta(weeks=max_hist_len)
            #print("Start: {}, end {}".format(start_date, end_date))
            transactions = g[ (g[date_column] >= start_date) & (g[date_column] <= end_date) ].copy()
            timespan_wks = int((transactions.iloc[-1,:][date_column] - transactions.iloc[0,:][date_column]).days / 7) + 1
            
            #print("Resulting frame length: {}".format(len(transactions)))
            #if len(transactions) > 1:
            #    print("yay")
                        
            #last_trans_dur_wks = int((timepoint - transactions.iloc[-1,:][date_column].tz_convert(None)).days / 7) + 1
            last_trans_dur_wks = int((timepoint - transactions.iloc[-1,:][date_column]).days / 7) + 1
            
            n_trans = len(transactions)
            
            #print("transactions {}".format(transactions))
            
            transactions.drop_duplicates(subset=['week_of_year'], keep='last', inplace=True)
            act_wks = len(transactions)

            nonact_wks = max(0, timespan_wks - act_wks)
            #print("start_week {}, end_week {}".format(start_week, end_week))
            #print("n_trans {}, act_wks {}, nonact_wks {}, timespan_wks {}".format(n_trans, act_wks, nonact_wks, timespan_wks))

            features.append((cid, end_date, last_trans_dur_wks, n_trans, act_wks, nonact_wks, timespan_wks))
        
        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(
        features, columns=[
            cid_column, 'last_trans_date', 'last_trans_dur_wks', 'n_trans', 'act_wks', 'nonact_wks', 'timespan_wks'
        ])

    return df_features

