import numpy as np
import matplotlib
from lmz import *
from scipy.stats import randint, uniform
import scipy
from scipy.stats.mstats import pearsonr
import math


def limit(scores_values,searchspace, paramname, fullsearchspace, thresh):

    # categorical data:
    if isinstance(fullsearchspace,list): 
        return  choosecategorical(scores_values, fullsearchspace)
   
    # have we converged already? if no lets proceed by gettin ght correlation
    CUTLEN = len(scores_values)
    data = np.array(scores_values[:CUTLEN])
    if sum(data[:,1] ==  data[:,1][0]) == CUTLEN:
        return [scores_values[0][1]]
    corr = pearsonr(data[:,0],data[:,1])[0]
    
    # fix the type of searchspave:
    searchspace = fixtype(searchspace)
    if  abs(corr) > thresh:
        searchspace =   half(searchspace, corr > 0)
        #print (paramname,searchspace.args, searchspace2.args)
        if abs(corr) > .5: # lets do it again if the correlation is good
            searchspace =   half(searchspace, corr > 0)
    return searchspace

def choosecategorical(scores_values, fullsearchspace): 
    scores, values = Transpose(scores_values)
    scores = np.array(scores)
    ma = -1
    va = ''
    for z in fullsearchspace:
        if z in values:
            vscore =np.mean(scores[[ v==z for v in values]])
            if vscore > ma:
                ma=vscore
                va = z
    return [va]

    

def fixtype(space):
    if isinstance(space, list):
        mi = min(space)
        if isinstance(space[0], float):
            return uniform(mi, max(space)-mi)
        else:
            return randint(mi,max(space)+1)
    return space


def half(space, up =  True):
    if isinstance(space.dist, scipy.stats._discrete_distns.randint_gen):
        a,b = space.args
        if up:
            return randint(math.floor( (a+b)/2 ) ,  b)
        else:
            return randint(a, math.ceil( (a+b)/2 ))
        
    elif isinstance(space.dist, scipy.stats._continuous_distns.uniform_gen):
        a,b = space.args
        if up:
            return uniform(a+b/2,b/2)
        else:
            return uniform(a, b/2)
    else:
        assert False, 'datatype not implemented'
