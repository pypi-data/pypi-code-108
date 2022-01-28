import pandas as pd
import numpy as np
import datetime

from sklearn.base import BaseEstimator, TransformerMixin


def get_time_of_day(timestamp, morning=12, evening=17):
    """
    """    
    if timestamp.hour < morning:
        return 'morning'
    if timestamp.hour > evening:
        return 'evening'
    return 'daytime'



def get_time_of_day_id(timestamp, morning=12, evening=17):
    """
    """
    if timestamp.hour < morning:
        return 0
    if timestamp.hour > evening:
        return 2
    return 1



def get_training_features_and_labels_tod(
    df, activity, 
    max_hist_len, cid_column, 
    activity_column, datetime_column, verbose=False
):
    """
    """
    
    print("Calculating time of day columns...")
    df_tod = pd.get_dummies( df[datetime_column].apply(lambda x: get_time_of_day(x)) )
    df = df.join( df_tod )

    print("Calculating groups...")
    df.loc[:,'observed'] = df[activity_column].apply(lambda x: 1 if x == activity else 0)
    
    dfg_customers = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])
    nc = len(dfg_customers)
    print("Number of customers: {:,} ({:,} rows)".format(nc, len(df)))
     
    features = []

    ii = 0
    tod = [0,0,0]

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        if len(g) > 1:

            ep = np.random.randint(1, len(g)-1) if len(g) > 2 else 1
            data = g.iloc[ max(ep-max_hist_len, 0):ep+1, ]
            
            ob_row = data.iloc[-1,:]
            
            observed = ob_row['observed']
            
            #tod[0] = data['morning'].sum()
            #tod[1] = data['daytime'].sum()
            #tod[2] = data['evening'].sum()
            tod[0] = data.apply(lambda x: x['morning']*x['observed'], axis=1).sum()
            tod[1] = data.apply(lambda x: x['daytime']*x['observed'], axis=1).sum()
            tod[2] = data.apply(lambda x: x['evening']*x['observed'], axis=1).sum()
            tod[0] = tod[0] - ob_row['morning']*ob_row['observed']
            tod[1] = tod[1] - ob_row['daytime']*ob_row['observed']
            tod[2] = tod[2] - ob_row['evening']*ob_row['observed']

            n_act = data['observed'].sum() - observed
            n_nonact = (len(data) - 1) - n_act
            last_email_date = data.iloc[-2,:][datetime_column]
            delta_t = data.iloc[-1,:][datetime_column] - last_email_date

            if verbose:
                print(cid)
                print(data)
                print('observed {}, delta_t {}, n_act {}, n_nonact {}, m {}, d {}, e {}, tod {}, ldate {}'.format(
                    observed, delta_t, n_act, n_nonact, 
                    tod[0], tod[1], tod[2], email_tod_id, last_email_date))

            features.append((cid, observed, delta_t, n_act, n_nonact, 
                             tod[0], tod[1], tod[2], 
                             last_email_date))

        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(features, columns=[cid_column,'observed','delta_t', 
                                                  'n_act', 'n_nonact', 
                                                  'morning', 'daytime', 'evening', 
                                                  'last_email_date'])
    df_features['delta_t'] = df_features['delta_t'].apply(
        lambda x: max(0, x.days + x.seconds/(24*60*60)))
    df_features['total_num_emails'] = df_features.apply(
        lambda x: x.n_act+x.n_nonact, axis=1)

    return df_features


"""
"""
class EmailTrainingFeaturesTODEstimator(BaseEstimator, TransformerMixin):
    
    def __init__(
        self, activity, max_hist_len, cid_column='Customer_ID', activity_column='Activity', datetime_column='Activity_Datetime'
    ):
        self.activity = activity
        self.max_hist_len = max_hist_len
        self.cid_column = cid_column
        self.activity_column = activity_column
        self.datetime_column = datetime_column
        
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[EmailTrainingFeaturesTODEstimator] transform {:,}...".format(len(X)))
        print(X[[self.cid_column, self.datetime_column, self.activity_column]].head())

        df = get_training_features_and_labels_tod(
            X,
            activity = self.activity,
            max_hist_len = self.max_hist_len,
            cid_column = self.cid_column,
            activity_column = self.activity_column,
            datetime_column = self.datetime_column
        )
        
        return df
    

"""
"""
def get_prediction_features_tod(
    df, activity, max_hist_len, 
    cid_column, activity_column, datetime_column, verbose=False
):
    
    print("Calculating time of day columns...")
    df_tod = pd.get_dummies( df[datetime_column].apply(lambda x: get_time_of_day(x)) )
    df = df.join( df_tod )

    print("Calculating groups...")
    df.loc[:,'observed'] = df[activity_column].apply(lambda x: 1 if x == activity else 0)
    dfg_customers = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])
    nc = len(dfg_customers)
    print("Number of customers: {:,} ({:,} rows)".format(nc, len(df)))
  
    features = []

    ii = 0
    tod = [0,0,0]

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        if len(g) >= 1:
            data = g.iloc[-max_hist_len:]
            #print(data)

            #tod[0] = data['morning'].sum()
            #tod[1] = data['daytime'].sum()
            #tod[2] = data['evening'].sum()
            tod[0] = data.apply(lambda x: x['morning']*x['observed'], axis=1).sum()
            tod[1] = data.apply(lambda x: x['daytime']*x['observed'], axis=1).sum()
            tod[2] = data.apply(lambda x: x['evening']*x['observed'], axis=1).sum()

            n_act = data['observed'].sum()
            n_nonact = len(data) - n_act
            last_email_date = data.iloc[-1,:][datetime_column]
           
            if verbose:
                print(data)
                print('n_act {}, n_nonact {}, m {}, d {}, e {}, ldate {}'.format(
                    n_act, n_nonact, tod[0], tod[1], tod[2], last_email_date))

            features.append((cid, n_act, n_nonact, 
                             tod[0], tod[1], tod[2], 
                             last_email_date))

        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(features, columns=[
        cid_column, 'n_act', 'n_nonact', 'morning', 'daytime', 'evening', 'last_email_date'
    ])
    df_features['total_num_emails'] = df_features.apply(lambda x: x.n_act+x.n_nonact, axis=1)

    return df_features


"""
"""
class EmailPredictionFeaturesTODEstimator(BaseEstimator, TransformerMixin):
    
    def __init__(
        self, activity, max_hist_len, cid_column, activity_column, datetime_column
    ):
        self.activity = activity
        self.max_hist_len = max_hist_len
        self.cid_column = cid_column
        self.activity_column = activity_column
        self.datetime_column = datetime_column
        
        return
    
    def fit(self, X, y=None):
        return
    
    def transform(self, X):
        
        assert isinstance(X, pd.DataFrame)
        
        print("[EmailPredictionFeaturesTODEstimator] transform {:,}...".format(len(X)))

        df = get_prediction_features_tod(
            X,
            activity = self.activity,
            max_hist_len = self.max_hist_len,
            cid_column = self.cid_column,
            activity_column = self.activity_column,
            datetime_column = self.datetime_column
        )
        
        return df
    
    

"""
"""
def get_training_features_basic(
    df, activity, max_hist_len = 16, 
    cid_column='External_ID', activity_column='Activity', datetime_column='Activity_Datetime'
):
    
    df['observed'] = df[activity_column].apply(lambda x: 1 if x == activity else 0)
    dfg_customers = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])
    nc = len(dfg_customers)
    print("Number of customers: {:,}".format(nc))
    
    features = []

    ii = 0

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        if len(g) > 1:
            #print(cid)
            ep = np.random.randint(1, len(g)-1) if len(g) > 2 else 1
            data = g.iloc[ max(ep-(max_hist_len+1), 0):ep+1, ]
            #print(data)

            observed = data.iloc[-1,:]['observed']

            n_act = data['observed'].sum() - observed
            n_nonact = (len(data) - 1) - n_act
            last_email_date = data.iloc[-1,:][datetime_column]
            delta_t = last_email_date - data.iloc[-2,:][datetime_column] 

            #print('observed {}, delta_t {}, n_act {}, n_nonact {}, ldate {}'.format(observed, delta_t, n_act, n_nonact, last_email_date))

            features.append((cid, observed, delta_t, n_act, n_nonact, last_email_date))

        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(features, columns=[cid_column,'observed','delta_t', 'n_act', 'n_nonact', 'last_email_date'])
    df_features['delta_t'] = df_features['delta_t'].apply(lambda x: max(0, x.days + x.seconds/(24*60*60)))
    df_features['total_num_emails'] = df_features.apply(lambda x: x.n_act+x.n_nonact, axis=1)

    return df_features


"""
"""
def get_prediction_features_basic(
    df, activity, timepoint, max_hist_len=16, 
    cid_column='External_ID', activity_column='Activity', datetime_column='Activity_Datetime'
):
    
    df['observed'] = df[activity_column].apply(lambda x: 1 if x == activity else 0)
    dfg_customers = df.sort_values(by=[cid_column, datetime_column]).groupby(by=[cid_column])
    nc = len(dfg_customers)
    print("Number of customers: {:,}".format(nc))
    
    features = []

    ii = 0

    for cid, g in dfg_customers:

        if ii % 5000 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))

        if len(g) >= 1:
            data = g.iloc[-max_hist_len:]
            #print(data)

            observed = data.iloc[-1,:]['observed']

            n_act = data['observed'].sum()
            n_nonact = len(data) - n_act
            last_email_date = data.iloc[-1,:][datetime_column]
            delta_t = timepoint - last_email_date 

            #print('observed {}, delta_t {}, n_act {}, n_nonact {}, ldate {}'.format(observed, delta_t, n_act, n_nonact, last_email_date))

            features.append((cid, observed, delta_t, n_act, n_nonact, last_email_date))

        ii = 1 + ii

    print("  {:,}/{:,} ({:.2f} %)".format(ii, nc, 100.0*ii/nc))
    
    df_features = pd.DataFrame(features, columns=[cid_column,'observed','delta_t', 'n_act', 'n_nonact', 'last_email_date'])
    df_features['delta_t'] = df_features['delta_t'].apply(lambda x: max(0, x.days + x.seconds/(24*60*60)))
    df_features['total_num_emails'] = df_features.apply(lambda x: x.n_act+x.n_nonact, axis=1)

    return df_features


"""
For a given time period, starting at [start_date] and lasting [timespan_wks] weeks:
Generate [num_emails] predictions for each customer, by taking the [num_emails] days
on which the model predicts the highest probability of activity.

max_slot_space - maximum number of predictions in each timeslot
disable_days - days for which never to generate a prediction
"""
def get_timeslots(
    df, 
    rm, 
    cid_column, covariate_columns, pred_threshold,
    start_date = None, 
    timespan_wks = 1, 
    num_emails = 1, 
    max_slot_space=1000000, disable_days = None
):
    
    days_in_timespan = 7*timespan_wks
    num_timeslots = 3*days_in_timespan
    
    frame = []
    timeslot_hist = [0] * num_timeslots
        
    if disable_days is not None:
        for dis in disable_days:
            timeslot_hist[dis*3:dis*3+3] = [max_slot_space] * 3

    timeslot_data = []

    nn = len(df)
    j = 0
    for _,row in df.iterrows():

        if j % 500 == 0:
            print("  {:,}/{:,} ({:.2f} %)".format(j, nn, 100.0*j/nn))
            
        if start_date is None:
            _start_date = row.last_email_date + datetime.timedelta(days=1)
        elif type(start_date) == str:
            _start_date = row[start_date]
        else:
            _start_date = start_date
            
        if type(num_emails) == str:
            _num_emails = row[num_emails]
        else:
            _num_emails = num_emails
        
        day_offset = int( (_start_date - row.last_email_date).days )
        if day_offset < 0:
            print("{} predicting in the past. start date is {}, but last email event date is: {}".format(_start_date, row.last_email_date))
            day_offset = 0

        frame = []
        for day in range(0,days_in_timespan):
            frame.append((day+day_offset, row.n_act, row.n_nonact, row.morning+1, row.daytime  , row.evening  , 0))
            frame.append((day+day_offset, row.n_act, row.n_nonact, row.morning  , row.daytime+1, row.evening  , 1))
            frame.append((day+day_offset, row.n_act, row.n_nonact, row.morning  , row.daytime  , row.evening+1, 2))

        df_to_pred = pd.DataFrame(frame, columns=['delta_t', 'n_act', 'n_nonact', 'morning', 'daytime', 'evening', 'tod'])

        rm.predict(df_to_pred, covariate_columns, pred_threshold=pred_threshold)
        #print(df_to_pred.head(21))
        
        rankings = df_to_pred.sort_values(by=['pred_ranking'], ascending=False)
        #print(rankings)
        for eid in range(_num_emails):
            best_day = int(rankings.iloc[eid,:].delta_t - day_offset)
            best_tod = int(rankings.iloc[eid,:].tod)
            best_slot = best_day*3 + best_tod
            propensity = rankings.iloc[eid,:].pred_ranking
            i = eid
            while timeslot_hist[best_slot] >= max_slot_space and i < len(df_to_pred):
                best_day = int(rankings.iloc[i,:].delta_t - day_offset)
                best_tod = int(rankings.iloc[i,:].tod)
                propensity = rankings.iloc[i,:].pred_ranking
                best_slot = best_day*3 + best_tod  
                i = 1 + i
            if i == len(df_to_pred):
                print("Timeslots full ({:,}/{:,})".format(j, nn))
                best_day = int(rankings.iloc[eid,:].delta_t - day_offset)
                best_tod = int(rankings.iloc[eid,:].tod)
                propensity = rankings.iloc[eid,:].pred_ranking
               
            best_slot = best_day*3 + best_tod
            #print(best_slot)
            timeslot_hist[best_slot] = 1 + timeslot_hist[best_slot]
            best_date = _start_date + datetime.timedelta(days=best_day)
            timeslot_data.append((
                row[cid_column], 
                eid, 
                best_date.strftime('%Y-%m-%d'), 
                best_date.weekday(), 
                best_tod,
                propensity
            ))
            #print("Best slot for {}: (day {}, tod {})".format(
            #    row[cid_column],  best_date.weekday(), best_tod
            #))
            
        j = 1 + j

    print("  {:,}/{:,} ({:.2f} %)".format(j, nn, 100.0*j/nn))
    print("Done.")
    
    #print(timeslot_data)

    df_out = pd.DataFrame(timeslot_data, columns=[
        cid_column, 'Email_ID', 'Date', 'Day_Of_Week', 'Time_Of_Day', 'Propensity'
    ])
    df_out.loc[:,'Date'] = pd.to_datetime(df_out['Date'], format='%Y-%m-%d')
    
    return df_out

"""
For a given time period, starting at [start_date]:
Generate [num_emails] predictions for each customer, by taking the [num_emails] days
on which the model predicts the highest probability of activity, and then spacing
them consecutive weeks apart.

max_slot_space - maximum number of predictions in each timeslot
disable_days - days for which never to generate a prediction
"""
def get_timeslots_consecutive_weeks(
    df, 
    rm, 
    cid_column, covariate_columns, pred_threshold,
    start_date = None, # Can be None, a datetime object, or a string denoting a column
    num_emails = 1, # Can be an integer, or a string denoting a column
    max_slot_space=1000000, disable_days = None
):
    df_out = get_timeslots(
        df,
        rm,
        cid_column, covariate_columns, pred_threshold,
        start_date = start_date,
        timespan_wks = 1,
        num_emails = num_emails,
        max_slot_space = max_slot_space,
        disable_days = disable_days
    )
    
    # We can use 'Email_ID' as the week identifier.
    df_out.loc[:,'Date'] = df_out.apply(lambda x: x.Date+datetime.timedelta(days=7*x.Email_ID), axis=1)
    
    return df_out