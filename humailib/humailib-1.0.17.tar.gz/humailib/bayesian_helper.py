# Bayesian weekday probability model

import pandas as pd
import numpy as np

import random

def histogr(df):
    vc = df.value_counts().sort_index()
    return vc# / vc.sum()

# Calculate likelihood:
# Lambda(D) := P(H | D) = Probability that the most popular day H:=argmax(H), given the
# most recent day D.

def CalcLikelihoodOverallMax(dfg_customers):
    ii = 0
    N = len(dfg_customers)
    likelihood = [np.zeros(7) for x in range(0,7)]
    cids = []
    hs = []
    for cid, g in dfg_customers:
        h = histogr(g['transaction_weekday'])
        hist = np.zeros(7)
        hist[h.index] = h.values

        mr_wday = int( g['transaction_weekday'].iloc[-1] )

        hist[mr_wday] = max(0, hist[mr_wday] - 1) # Subtract most recent transaction
        #print(hist)
        most_popular = np.argwhere(hist == np.amax(hist))
        most_popular = most_popular.flatten().tolist()
        #print(most_popular)
        most_popular = int(random.choice(most_popular))

        #print('mr: {0}, pop: {1}'.format(mr_wday, most_popular))

        likelihood[mr_wday][most_popular] = 1 + likelihood[mr_wday][most_popular]

        ii = 1 + ii
        
        if ii % 1000 == 0:
            print('{0}/{1}'.format(ii, N))
            
        cids.append(cid)
        hs.append(hist)

    for i in range(0,len(likelihood)):
        ss = np.sum( likelihood[i] )
        if ss > 0.0:
            likelihood[i] = likelihood[i] / ss
            
    return likelihood, cids, hs

# Calculate likelihood:
# Lambda(D) := P(H | D) = Probability that the most popular day of the last m days,
# H := argmax(H[-m:]), given the most recent day D.

def CalcLikelihoodRecentMax(dfg_customers, m = 5):
    ii = 0
    N = len(dfg_customers)
    likelihood = [np.zeros(7) for x in range(0,7)]
    cids = []
    hs = []
    for cid, g in dfg_customers:
        h = histogr(g['transaction_weekday'].iloc[-m:])
        hist = np.zeros(7)
        hist[h.index] = h.values
        #print('Hist: {0}'.format(hist))
        
        mr_wday = int( g['transaction_weekday'].iloc[-1] )
        hist[mr_wday] = max(0, hist[mr_wday] - 1) # Subtract most recent transaction
        
        #print('Most recent m: {0}'.format(g['transaction_weekday'].iloc[-m:].values))
        #print('All: {0}'.format(g['transaction_weekday'].values))
        most_popular = np.argwhere(hist == np.amax(hist))
        most_popular = most_popular.flatten().tolist()
        #print(most_popular)
        most_popular = int(random.choice(most_popular))

        #print('mr: {0}, pop: {1}'.format(mr_wday, most_popular))

        likelihood[mr_wday][most_popular] = 1 + likelihood[mr_wday][most_popular]

        ii = 1 + ii
        
        if ii % 1000 == 0:
            print('{0}/{1}'.format(ii, N))
            
        cids.append(cid)
        hs.append(hist)

    for i in range(0,len(likelihood)):
        ss = np.sum( likelihood[i] )
        if ss > 0.0:
            likelihood[i] = likelihood[i] / ss
            
    return likelihood, cids, hs

# Calculate histories only:

def CalcHistories(dfg_customers, m = 5):
    ii = 0
    N = len(dfg_customers)
    cids = []
    hs = []
    for cid, g in dfg_customers:
        h = histogr(g['transaction_weekday'].iloc[-m:])
        hist = np.zeros(7)
        hist[h.index] = h.values
        
        # Get most recent.
        mr_wday = int( g['transaction_weekday'].iloc[-1] )
        hist[mr_wday] = max(0, hist[mr_wday] - 1) # Subtract most recent transaction
        
        ii = 1 + ii
        if ii % 1000 == 0:
            print('{0}/{1}'.format(ii, N))
            
        cids.append(cid)
        hs.append(hist)
            
    return cids, hs

def BayesianProbFromHist(prior, likelihood, hist=[]):
    
    if len(hist) == 0:
        return prior

    n = len(prior)
    p_d_h = [0] * 7
    
    most_popular = np.argwhere(hist == np.amax(hist))
    most_popular = most_popular.flatten().tolist()
    #print(most_popular)
    most_popular = int(random.choice(most_popular))
    
    for d in range(0,7):
        p_d_h[d] = likelihood[d][most_popular] * prior[d]

    return p_d_h 
    
    
    

    