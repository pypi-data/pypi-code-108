import pandas as pd
import numpy as np
from scipy import stats
import datetime
import os
import math
import pickle
import matplotlib.pyplot as plt 

from datetime import datetime, timedelta

import lifelines
from lifelines import AalenAdditiveFitter
from lifelines import CoxPHFitter

class HumaiPropHazardsFeatureGen:

    def __init__(self):
        self.dataset = None
        return

    def generate(self, df_trans, date_column='Datetime', cid='Email', min_trans=2, verbose=True):

        df_trans['Datetime'] = pd.to_datetime(df_trans['Datetime'], format='%Y-%m-%dT%H:%M:%S.000Z')
        if verbose:
            print('[HumaiProportionalHazardsModel] Date range from {0} to {1}'.format(df_trans['Datetime'].min(), df_trans['Datetime'].max()))

        if verbose:
            print("  Calculating time between transactions...")

        # Define subset if necessary
        customers_unique = df_trans[cid].unique()
        # Set-up dataframe with data
        df_setup = df_trans[df_trans[cid].isin(customers_unique)]
        # Define transaction_number_renter: Rank transactions per renter
        # 1.Sort on renter_number and transaction_end
        # 2.Rank records
        df_setup.sort_values(by=[cid, date_column], inplace=True)
        groups = df_setup.groupby(by=[cid])[date_column]
        df_setup.loc[:,'transaction_number_customer']=groups.rank(method='first')
        # Calculate time_between_transactions by sorting and using diff() function
        df_setup['time_between_transactions'] = df_setup.sort_values(by=[cid,'transaction_number_customer']).loc[:,date_column].diff()

        # Set time_between_transactions as NaT for first transaction
        mask_first_trans = df_setup.transaction_number_customer==1
        tmp = df_setup['time_between_transactions'].where(~mask_first_trans,other=pd.Timedelta(None))
        #tmp = df_setup['time_between_transactions'].where(~mask_first_trans,other=0.0)
        df_setup['time_between_transactions'] = tmp

        # Create column to days between transactions and version as float
        df_setup.loc[:,'days_between_transactions'] = df_setup['time_between_transactions'].apply(lambda x: max(0, x.ceil(freq='D').days))
        df_setup['days_between_transactions_float'] = df_setup['time_between_transactions'].apply(lambda x: max(0, x.days + x.seconds/(24*60*60)))

        if verbose:
            print("  Getting first transaction...")
        # Add column with first transaction
        a = df_setup[df_setup.transaction_number_customer==1].loc[:,[cid,date_column]]
        b = df_setup
        df_setup = b.merge(how='left',right=a, left_on=cid, right_on=cid,suffixes=('','_first'))

        if verbose:
            print("  Discarding customers with fewer than {0} transactions...".format(min_trans))

        # Mask out the NaTs (first transactions)
        #mask = df_setup.transaction_number_renter == 1
        #df_setup.days_between_transactions_float[mask] = 0.0

        # Keep customers who have performed at least 2 transactions (i.e. they are not right-censored)
        grp = df_setup.groupby(cid)
        tmp = grp.filter(lambda x: x['Transaction_ID'].count() >= min_trans)
        grp = tmp.groupby(by=[cid])

        cids = grp.apply(lambda x: x.name).values

        # Boolean (0,1): Whether total number of transactions > 1, i.e. first-time renters = 0, others = 1
        E = grp.transaction_number_customer.apply(lambda x: min(1, x.count()-1))
        if verbose:
            print("  E...")
            E.head(10)

        #rates = grp.days_between_transactions_float.apply(lambda x: (x.count()+1)/x.sum())
        #if verbose:
        #    print("  rates...")
        #    rates.head(10)

        # Average days between transactions
        days_mean = grp.days_between_transactions_float.mean()
        #days_mean = grp.days_between_transactions_float.median()
        if verbose:
            print("  days_mean...")
            days_mean.describe()

        #days_var = grp.days_between_transactions_float.var()
        days_var = grp.days_between_transactions_float.quantile(0.75) - grp.days_between_transactions_float.quantile(0.25)
        days_var.fillna(value=0,inplace=True)
        if verbose:
            print("  days_var...")
            days_var.head(10)

        last_trans_date = grp.Datetime.last()
        if verbose:
            print("  last transaction date...")
            last_trans_date.head(10)

        # Days between last two transactions
        T = grp.days_between_transactions_float.last()
        if verbose:
            print("  T...")
            T.describe()

        # Total number of transactions
        tcount = grp.transaction_number_customer.count()
        if verbose:
            print("  tcounts...")
            tcount.describe()

        tnumitemstotal = grp['Num_Items_Purchased'].sum()
        if verbose:
            print("  tnumitemstotal...")
            tnumitemstotal.describe()

        frequent_customers = pd.Series(data=[0]*len(tcount))
        mask = (tcount > 5)
        frequent_customers[mask.values] = 1
        mask = (tcount > 10)
        frequent_customers[mask.values] = 2

        #dataset = pd.DataFrame({'frequent_customers' : frequent_customers.values, 'days_mean' : days_mean.values, 'days_var' : days_var.values, 'total' : tcounts.values, 'T' : T.values, 'E' : E.values})
        self.dataset = pd.DataFrame({cid : cids,
                                'last_transaction_date' : last_trans_date.values,
                                'frequent_customers' : frequent_customers.values,
                                'tnumitemstotal' : tnumitemstotal,
                                'days_mean' : days_mean,
                                'days_var' : days_var,
                                'tcount' : tcount,
                                'T' : T.values, 
                                'E' : E.values})

        return self.dataset

    def save(self, filename):
        self.dataset.to_csv(filename)
        #pickle.dump([self.dataset], open(filename, "wb"))
        return

    def load(self, filename):
        self.dataset = pd.read_csv(filename)
        self.dataset['last_transaction_date'] = pd.to_datetime(self.dataset['last_transaction_date'], format='%Y-%m-%d %H:%M:%S')
        #self.dataset = pickle.load( open(filename, "rb") )
        return


class HumaiPropHazardsModel:

    def __init(self):
        self.cph = None
        self.features = None
        
    def learn(self, dataset, features = ['frequent_customers', 'tnumitemstotal', 'days_mean', 'days_var'], 
            duration_col='T', event_col='E', step_size=0.25, 
            verbose=True):

        self.features = features.copy()
        ext_features = features.copy()
        ext_features.extend([duration_col, event_col])
    
        self.cph = CoxPHFitter()
        self.cph.fit(dataset[ext_features], duration_col=duration_col, 
                     event_col=event_col, 
                     step_size=0.25, show_progress=verbose)

        if verbose:
            self.cph.print_summary()

    def predict(self, dataset, features = ['frequent_customers', 'tnumitemstotal', 'days_mean', 'days_var'], threshold=0.8):

        if self.cph is None or self.features is None:
            return None

        if features is None:
            features = self.features

        pred = self.cph.predict_survival_function(dataset[features])

        def findFirstIndex(A, p):
            i = 0
            for a in A:
                if a < p:
                    return i
                i = 1 + i

            return len(A)-1

        #out[:][0].index.values[pred[3]]

        #print(pred)

        predictions = [pred.iloc[:,i].index.values[findFirstIndex(pred.iloc[:,i], threshold)] for i in range(0, pred.shape[1])]

        deltas = [timedelta(days=x) for x in predictions]
        dates = dataset['last_transaction_date'] + deltas

        return predictions, dates

    def save(self, filename):
        pickle.dump([self.cph, self.features], open(filename, "wb"))
        return

    def load(self, filename):
        self.cph, self.features = pickle.load( open(filename, "rb") )
        return

    

    

    


        

        

