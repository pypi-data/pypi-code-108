import pandas as pd
import numpy as np
import datetime

# Clip [a,b) to lie within [s,t)
def clip_range(a, b, s, t):
    if b <= s or a >= t:
        return pd.NaT, pd.NaT, True
    
    return min(max(a, s), t), min(max(b, s), t), False

def get_date_range_for_lifecyclestage(df_lifecycle, stages=['hl'], timeframe=None):

    df = df_lifecycle
    
    wk_cols = []

    for c in list(df):
        if type(c) == str and 'week_' in c:
            wk_cols.append(c)
            
    df_out = df.copy()

    clipped = []
    start_dates = []
    end_dates = []
        
    n = len(df_out)
    for i in range(n):
        row = df_out.iloc[i,:]
        
        if i % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(i, n, 100.0*i/n))
        
        #print("[{},{})".format(tf_start_wk, tf_end_wk))
        
        cur_stage = 'no_stage'
        stage_start_wk = -1
        stage_end_wk = -1
        # Half-open [stage_start_wk, stage_end_wk)
        for c in wk_cols:
            if row[c] in stages and cur_stage not in stages:
                stage_start_wk = int(c.split('_')[1])
            elif row[c] not in stages and cur_stage in stages:
                stage_end_wk = int(c.split('_')[1])
            cur_stage = row[c]
            
        # Half open interval
        stage_start_date = row.last_trans_date + datetime.timedelta(days=7*(stage_start_wk-1))
        stage_end_date = row.last_trans_date + datetime.timedelta(days=7*(stage_end_wk-1))
        
        stage_start_date_clipped = stage_start_date
        stage_end_date_clipped = stage_end_date
        clip = False
        if timeframe is not None:
            stage_start_date_clipped, stage_end_date_clipped, clip = clip_range(
                stage_start_date, stage_end_date, 
                timeframe[0], timeframe[1]
            )
        
        #print("[{},{}) clipped to [{},{}) gets [{},{})".format(
        #    stage_start_date, stage_end_date, timeframe[0], timeframe[1], stage_start_date_clipped, stage_end_date_clipped
        #))
        
        clipped.append(clip)
        start_dates.append( stage_start_date_clipped )
        end_dates.append( stage_end_date_clipped )
        
    print("  {:,}/{:,} ({:.2f} %)".format(n, n, 100.0))
    
    #print(start_dates[:10])
        
    stages_str = '_'.join(stages)
    df_out.loc[:,'{}_clipped'.format(stages_str)] = clipped
    df_out.loc[:,'{}_start_date_clipped'.format(stages_str)] = start_dates
    df_out.loc[:,'{}_end_date_clipped'.format(stages_str)] = end_dates
    
    return df_out


def filter_customers_in_lifecycle_stage(
    df_features, 
    df_lifecycle, 
    max_emails_per_customer=3, 
    stages=['hl'], 
    timeframe=None, 
    cid_column='Customer_ID'
):
    
    assert (isinstance(stages, list)), "stages argument should be a list."
    
    # Get active_frame (start and end date) for all customers in lifecycle stage [stage], within a given timeframe
    df_lifecycle_clipped = get_date_range_for_lifecyclestage(df_lifecycle, stages=stages, timeframe=timeframe)
    
    # Remove all customers that didn't make the cut from the lifecycle
    df_lifecycle_clipped = df_lifecycle_clipped.drop(index=df_lifecycle_clipped[df_lifecycle_clipped['hl_clipped']].index)
    df_lifecycle_clipped.reset_index(inplace=True)

    df_to_pred = df_features.copy()
    df_to_pred.set_index(cid_column, inplace=True)
    
    # Keep only those customers in df_features that are in lifecycle frame, put in df_to_pred
    print("Before filtering {:,}".format(len(df_to_pred)))

    indices = df_to_pred.index.intersection(df_lifecycle_clipped[cid_column])
    df_to_pred = df_to_pred.reindex(indices)

    print("After filtering {:,}".format(len(df_to_pred)))
    
    df_lifecycle_clipped.set_index(cid_column, inplace=True)
    
    # Convert start and end dates of active_frame to start date and num emails
    df_to_pred.loc[indices,'pred_start_date'] = df_lifecycle_clipped.loc[indices, 'hl_start_date_clipped']
    df_to_pred.loc[indices,'pred_end_date'] = df_lifecycle_clipped.loc[indices, 'hl_end_date_clipped']
    df_to_pred.loc[indices,'num_emails_to_predict'] = df_lifecycle_clipped.loc[indices, :].apply(
        lambda x: min(max_emails_per_customer, int((x['hl_end_date_clipped'] - x['hl_start_date_clipped']).days / 7 + 1)), 
        axis=1
    )
    
    df_lifecycle_clipped.reset_index(inplace=True)
    df_to_pred.reset_index(inplace=True)
    
    return df_to_pred