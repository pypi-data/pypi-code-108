import pandas as pd
import numpy as np
import datetime
import random
from timeit import default_timer as timer

from dateutil.relativedelta import relativedelta

import sklearn
import lifelines
from lifelines import AalenAdditiveFitter
from lifelines import CoxPHFitter


def predict_propensity_to_buy(
    df,
    start_date,
    end_date,
    covariate_columns,
    rm,
    pred_threshold,
    dur_column='last_trans_dur_wks',
    cid_column='Customer_ID',
    batch_size = 1000,
    verbose=False
):
    n = len(df)
    propensities = []
    prediction_week_range = int( (end_date - start_date) / pd.to_timedelta(7, unit='D') )
    ofs = 0
    while ofs < n:
        print("{:,}/{:,} ({:.2f}%)".format(ofs, n, float(ofs)*100.0/n))

        cols = [c for c in covariate_columns if c != dur_column]
        end = min(n, ofs+batch_size)

        rows = df.iloc[ofs:end,:]
        to_pred_data = []
        for i in range(end-ofs):
            row = rows.iloc[i,:]
            delta = (start_date - row['last_trans_date']) / pd.to_timedelta(7, unit='D')
           
            for wk in range(prediction_week_range):
                to_pred_data.append(tuple([row[cid_column], delta+wk] + row[cols].tolist()))

        df_to_pred = pd.DataFrame(to_pred_data, columns=[cid_column,dur_column]+cols)
        rm.predict(df_to_pred, covariate_columns, pred_threshold=pred_threshold)
        
        for cid, df_propensities in df_to_pred.groupby(by=cid_column):
            
            pred_propensities = np.float128(df_propensities['pred_ranking'].to_numpy())

            if verbose:
                print("Propensities {}: {}".format(row[cid_column], pred_propensities))

            propensities.append(tuple([cid] + pred_propensities.tolist()))
            
        ofs = batch_size + ofs
    
    dates=[start_date+pd.to_timedelta(i*7, unit='D') for i in range(0, prediction_week_range) ]
    columns=['propensity_to_buy_{}'.format(date.strftime("%Y%m%d")) for date in dates]
    df_out = pd.DataFrame(propensities, columns=[cid_column]+columns)
    
    return df_out


def predict_lifecycles(
    df, 
    prediction_date,
    num_months_ahead,
    lhood_columns, 
    prior_columns, 
    rm, 
    cph, 
    pred_threshold, 
    dur_column='last_trans_dur_wks',
    cid_column='Customer_ID', 
    batch_size=1000,
    delay_until_max=True, 
    verbose=False
):
    
    n = len(df)
    out_data = []
    
    start_date = datetime.datetime(year=prediction_date.year, month=prediction_date.month, day=prediction_date.day) #
    end_date = start_date + relativedelta(months=num_months_ahead)
    prediction_week_range = int( (end_date - start_date) / pd.to_timedelta(7, unit='D') )
    
    ofs = 0
    print("{:,}/{:,} ({:.2f}%)".format(ofs, n, float(ofs)*100.0/n))
    while ofs < n:

        t0 = timer()
        
        l_cols = [c for c in lhood_columns if c != dur_column]
        p_cols = [c for c in prior_columns if c != dur_column]
        end = min(n, ofs+batch_size)

        rows = df.iloc[ofs:end,:]
        batch_size = end-ofs
        
        ##
        ## Get likelihood.
        
        to_pred_data = []
        for i in range(batch_size):
            row = rows.iloc[i,:]
            within_week_offset, weeks_to_start = np.modf((start_date - row['last_trans_date']) / pd.to_timedelta(7, unit='D'))
            weeks_to_start = int(weeks_to_start)

            weeks = weeks_to_start + prediction_week_range
            for wk in range(weeks):
                #print(f'weeks={weeks}')
                to_pred_data.append(tuple([row[cid_column], within_week_offset+wk] + row[l_cols].tolist()))

        df_to_pred = pd.DataFrame(to_pred_data, columns=[cid_column, dur_column]+l_cols)
        rm.predict(df_to_pred, [dur_column]+l_cols, pred_threshold=pred_threshold)
        
        likelihoods = []
        for cid, df_propensities in df_to_pred.groupby(by=cid_column):
            
            propensities = np.float128(df_propensities['pred_ranking'].to_numpy())

            if verbose:
                print("Propensities {}: {}".format(row[cid_column], pred_propensities))

            #print(f'propensities n={len(propensities)}')
            likelihoods.append(tuple(propensities.tolist()))
            
        ##
        ## Get prior.
        
        to_pred_times = []
        weeks = 0
        wk_offset = 0
        for i in range(batch_size):
            row = rows.iloc[i,:]
            within_week_offset, weeks_to_start = np.modf((start_date - row['last_trans_date']) / pd.to_timedelta(7, unit='D'))
            weeks_to_start = int(weeks_to_start)

            if weeks_to_start + prediction_week_range > weeks:
                weeks = weeks_to_start + prediction_week_range
                wk_offset = within_week_offset
                
        priors = cph.predict_survival_function(
            rows.loc[:,p_cols], 
            times=[wk_offset+wk for wk in range(weeks)],
        )
        
        ##
        ## Calculate lifecycle stages
        
        for i in range(batch_size):
            row = rows.iloc[i,:]

            #print(f'cid {row[cid_column]}')

            prior = np.array( priors.iloc[:,i] )
            likelihood = np.array( likelihoods[i] )
            window = min(len(prior), len(likelihood))
            likelihood = likelihood[:window]
            prior = prior[:window]
            
            ml = max(likelihood)
            if delay_until_max:
                idx = random.choice( [ii for ii,j in enumerate(likelihood) if j==ml] )
                prior[:idx] = 1.0
            
            posterior = (likelihood * prior).tolist()
            if len(posterior) < prediction_week_range:
                print(f'i={i} -> len(posterior) < prediction_week_range, len(prior)={len(prior)}, len(likelihood)={len(likelihood)}')
            sgn = [0]
            sgn.extend(np.sign(np.diff(posterior)))

            # jb - just bought
            # nt - neutral
            # go - growing opportunity
            # hl - highest likelihood
            # dc - declining
            # ls - loss
            hl_ids = [ii+1 for ii,p in enumerate(posterior[1:]) if p==posterior[0]]

            stage = np.array(['nt'] * len(posterior))
            stage = ['go' if s > 0 else m for s,m in zip(sgn,stage)]
            stage = ['dc' if s < 0 else m for s,m in zip(sgn,stage)]
            state = 'na'
            for ii,s in enumerate(stage):
                    
                if state == 'go' and s != 'go':
                    stage[ii] = 'hl'
                    state = 'na'
                    if s == 'nt':
                        state = 'go'

                if state != 'go' and s == 'go':
                    state = 'go'
                    
            stage[0] = 'jb'
            for hl_id in hl_ids:
                stage[hl_id] = 'hl'
                
            hl_ids = [ii for ii,s in enumerate(stage) if (s == 'hl' or s == 'hl+jb')]
            if len(hl_ids) > 0:
                stage = [
                    'ls' if (ii > hl_ids[-1] and ii > row['death_from']) else \
                    m for s,ii,m in zip(sgn,range(0,len(sgn)), stage)
                ]
            else:
                stage = [
                    'ls' if (ii > row['death_from']) else \
                    m for s,ii,m in zip(sgn,range(0,len(sgn)), stage)
                ]
                            
            try:
                past_stages = stage[0:-prediction_week_range]
                current_stage = stage[-prediction_week_range:-prediction_week_range+1][0]
                future_stages = stage[-prediction_week_range+1:]
            except:
                print(f'i={i}, prediction_week_range={prediction_week_range}, stage={stage} (n={len(stage)})')
                
                
            weeks_to_past_hl = np.nan
            for ii,s in enumerate(past_stages[::-1]):
                if s == 'hl':
                    weeks_to_past_hl = ii+1
                    break
            weeks_to_future_hl = np.nan
            for ii,s in enumerate(future_stages):
                if s == 'hl':
                    weeks_to_future_hl = ii+1
                    break
            
            if np.isnan(weeks_to_past_hl) and np.isnan(weeks_to_future_hl):
                weeks_to_next_hl = np.nan
            elif np.isnan(weeks_to_past_hl):
                weeks_to_next_hl = weeks_to_future_hl
            elif np.isnan(weeks_to_future_hl):
                weeks_to_next_hl = -weeks_to_past_hl
            elif weeks_to_past_hl < weeks_to_future_hl:
                weeks_to_next_hl = -weeks_to_past_hl
            else:
                weeks_to_next_hl = weeks_to_future_hl
            
            #print(f'past stages {past_stages}')
            #print(f'cur stage {current_stage}')
            #print(f'future stages {future_stages}')
            
            past_max_posterior = np.nan
            current_posterior = np.nan
            future_max_posterior = np.nan
            
            if len(posterior[0:-prediction_week_range]) > 0:
                past_max_posterior = max(posterior[0:-prediction_week_range])
            current_posterior = posterior[-prediction_week_range:-prediction_week_range+1][0]
            if len(posterior[-prediction_week_range+1:]) > 0:
                future_max_posterior = max(posterior[-prediction_week_range+1:])
            
            peak_in_future = True if (('hl' in future_stages) or ('go' in future_stages)) else False
            out_data.append(tuple([
                row[cid_column],
                start_date,
                row['last_trans_date'],
                max(posterior) > pred_threshold,
                True if ('hl' in past_stages or 'hl+jb' in past_stages) else False,
                past_max_posterior,
                current_stage,
                current_posterior,
                peak_in_future,
                future_max_posterior,
                weeks_to_next_hl,
            ]))
        
        ofs = batch_size + ofs        

        t1 = timer()
        print("{:,}/{:,} ({:.2f}%), last batch took {}".format(ofs, n, float(ofs)*100.0/n, str(datetime.timedelta(seconds=(t1-t0)))))
        
        
    date_str = start_date.strftime('%Y%m%d')
    df_out = pd.DataFrame(out_data, columns=[cid_column]+[
        'date',
        'last_trans_date',
        'is_high_propensity_customer',
        'peak_in_past','max_past_posterior_propensity',
        'lifecycle_stage_at_date','posterior_propensity_at_date',
        'peak_in_future','max_future_posterior_propensity',
        'weeks_to_next_peak',
    ])
        
    print("{:,}/{:,} ({:.2f}%)".format(i, n, 100))
        
    return df_out
