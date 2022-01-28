import pandas as pd
import numpy as np

def GetWeekdaySequencesIncNonOpens(dfg_customers, weekday_column='transaction_weekday', activity_column='activity', min_seq_len = 5, max_seq_len=15, verbose=False):
    
    num_days = 8  # 7 + non-open
    
    customers = []
    sequences = []
    seqlens = []
    
    ii = 0
    nc = len(dfg_customers)
    
    for cid, g in dfg_customers:
        
        n = 0
        label = np.zeros(num_days)
        
        if (len(g[weekday_column]) >= min_seq_len):
            
            if verbose:
                print(g[weekday_column].iloc[:].values)
                print(g[activity_column].iloc[:].values)
                
            if g[weekday_column].iloc[-max_seq_len:].isnull().any():
                print("NaN detected for customer: {0}".format(cid))
                print(g[weekday_column].iloc[:].values)
                print(g[activity_column].iloc[:].values)
                g[weekday_column].fillna(7, inplace=True)
            
            h = [7 if (a=='BROADCASTS' or x==7) else int(x) for a,x in 
                 zip(g[activity_column].iloc[-max_seq_len:].values, 
                     g[weekday_column].iloc[-max_seq_len:].values)]
            
            # If the sequence consists of nothing but non-opens, make
            # its length 0.
            if np.min(h) == 7:
                n = 1 #0
            else:
                n = len(h)
                
            # If h is less than [time_steps] in length, pad it with last element
            if len(h) < max_seq_len:
                
                nn = max(0, max_seq_len - len(h))
                h.extend([h[-1] for i in range(0,nn)])
                
            #if n > 0:
            if verbose:
                print("h={0} (n={1})".format(h, n))
                
            customers.append(cid)
            sequences.append(np.array(h))
            seqlens.append(n)
        
        ii = 1 + ii
        
        if ii % 1000 == 0:
            print("  {0}/{1}".format(ii, nc))   
        
    return customers, sequences, seqlens


def GetWeekdaySequencesAndLabelsIncNonOpens(dfg_customers, weekday_column='transaction_weekday', activity_column='activity', min_seq_len = 5, max_seq_len=15, verbose=False):
    
    num_days = 8  # 7 + non-open
    
    customers = []
    sequences = []
    labels = []
    labelid = []
    seqlens = []
    
    ii = 0
    nc = len(dfg_customers)

    for cid, g in dfg_customers:

        
        n = 0
        label = np.zeros(num_days)
        
        if (len(g[weekday_column]) > min_seq_len):
            
            if verbose:
                print(g[weekday_column].iloc[:].values)
                print(g[activity_column].iloc[:].values)
                
            if g[weekday_column].iloc[-(max_seq_len+1):-1].isnull().any():
                print("NaN detected for customer: {0}".format(cid))
                print(g[weekday_column].iloc[:].values)
                print(g[activity_column].iloc[:].values)
                g[weekday_column].fillna(7, inplace=True)
            
            h = [7 if (a=='BROADCASTS' or x==7) else int(x) for a,x in 
                 zip(g[activity_column].iloc[-(max_seq_len+1):-1].values, 
                     g[weekday_column].iloc[-(max_seq_len+1):-1].values)]
                
            l = int(g[weekday_column].iloc[-1:].values[0]) if g[activity_column].iloc[-1] != 'BROADCASTS' else 7
            label[ l ] = 1
            
            # If the sequence consists of nothing but non-opens, make
            # its length 0.
            if np.min(h) == 7:
                n = 1 #0
            else:
                n = len(h)
            
            # If h is less than [time_steps] in length, pad it with last element
            if len(h) < max_seq_len:
                
                nn = max(0, max_seq_len - len(h))
                h.extend([h[-1] for i in range(0,nn)])
                    
            #if n > 0:
            if verbose:
                print("h={} -> {}: {} (n={})".format(h, l, label, n))
                
            customers.append(cid)
            sequences.append(np.array(h))
            seqlens.append(n)
            labels.append(np.array(label))
            labelid.append(l)

        ii = 1 + ii
        
        if ii % 1000 == 0:
            print("  {0}/{1}".format(ii, nc))
        
    return customers, sequences, labels, labelid, seqlens


def sqm_create_training_data(deliveries, 
                             weekday_column='transaction_weekday', 
                             activity_column='activity', 
                             min_seq_len = 5, 
                             max_seq_len=15, 
                             verbose=False):


    return
