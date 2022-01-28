import numpy as np
import pandas as pd
import scipy
from scipy import stats


def  MultiTrCorrPvalue(x, lags=1):


    """
    x : array-like 
        Data matrix to be analyzed or residuals to be tested when modeling.
    
    lags: int
        Max number of  the lag
    
    Returns
    -------
    tr_stats : array
        statistic for trace of correlation matrix
    pvalues : array
        P-value of the tr_stats
    
    """

    pvalues = []
    tr_stats = []
    for nlags in range(1, lags+1):
        tr_stat, pvalue = statf(x, nlags=nlags)
        tr_stats.append(tr_stat)
        pvalues.append(pvalue)

    import matplotlib.pyplot as plt
      
    Lag=range(1, lags+1)
    from matplotlib.ticker import MultipleLocator
    xmajorLocator = MultipleLocator(1)
    fig = plt.figure()
    ax =fig.add_subplot(111)
    ax.xaxis.set_major_locator(xmajorLocator)
    plt.plot(Lag, pvalues, linestyle='', marker='.')
    plt.xlabel('Lag')
    plt.ylabel('P-values')
    plt.axhline(y=0.05, linestyle=':', color='b')
    plt.title('P-value plot for trace of sample correlation matrix')
    plt.show()
        
    return   np.array(tr_stats), np.array(pvalues)

    
def  statf(x, nlags):

    #from statsmodels.tools.tools import chain_dot

    
    u = np.asarray(x)
    acov_list = _compute_acov(u)
    cov0_inv = scipy.linalg.inv(acov_list[0])
    nobs = len(x)
    K = x.shape[1]
    # K-dim TS
    ct = acov_list[nlags]
    #to_add = np.trace(chain_dot(ct.T, cov0_inv, ct, cov0_inv))
    to_add = np.trace(ct.T @ cov0_inv @ ct @ cov0_inv)
    to_add /= (nobs - nlags)
    statistic = to_add*nobs**2 
    df = K**2 
    dist = stats.chi2(df)
    pvalue = dist.sf(statistic)
        
    return   statistic, pvalue


def _compute_acov(x):
     x = x - x.mean(0)
     leng=len(x)

     result = []
     for lag in range(leng):
         if lag > 0:
             r = np.dot(x[lag:].T, x[:-lag])
         else:
             r = np.dot(x.T, x)

         result.append(r)

     return np.array(result) / len(x)

