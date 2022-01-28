import numpy as np
import pandas as pd
import scipy
from scipy import stats


def  MultiQpvalue_plot(x, p=0,q=0, noestimatedcoef=0, nolags=1, modified=True):


    """
    x : array-like 
        Data matrix to be analyzed or residuals to be tested when modeling.
    noestimatedcoef: int
        Number of estimated coefficients for residuals; but it is 0 before modeling.   
    nolags: int
        Max number of added terms in portmanteau statistic.  In general, nolags  should
        be greater than p+q for VARMA(p, q) models.
    modified: bool, default True, namely, Ljung-Box; if False, Li-McLeod.
    Returns
    -------
    qstats : array
        portmanteau statistic for autocorrelation parameters
    pvalues : array
        P-value of the portmanteau statistic
    
    """

    pvalues = []
    qstats = []
    for nlags in range(p+q+1, nolags+1):
        statistic, pvalue = qstatf(x, noestimatedcoef, nlags=nlags, adjusted=modified)
        qstats.append(statistic)
        pvalues.append(pvalue)

    import matplotlib.pyplot as plt
      
    Lag=range(p+q+1, nolags+1)
    from matplotlib.ticker import MultipleLocator
    xmajorLocator = MultipleLocator(1)
    fig = plt.figure()
    ax =fig.add_subplot(111)
    ax.xaxis.set_major_locator(xmajorLocator)
    plt.plot(Lag, pvalues, linestyle='', marker='.')
    plt.xlabel('Lag')
    plt.ylabel('p-values')
    plt.axhline(y=0.05, linestyle=':', color='b')
    plt.title('P-value plot for portmanteau statistic')
    plt.show()
        
    return   np.array(qstats), np.array(pvalues)

    
def  qstatf(x, noestimatedcoef, nlags, adjusted):

    #from statsmodels.tools.tools import chain_dot

    statistic = 0
    u = np.asarray(x)
    acov_list = _compute_acov(u)
    cov0_inv = scipy.linalg.inv(acov_list[0])
    nobs = len(x)
    K = x.shape[1]
    # K-dim TS
    for t in range(1, nlags+1):
         ct = acov_list[t]
         #to_add = np.trace(chain_dot(ct.T, cov0_inv, ct, cov0_inv))
         to_add = np.trace(ct.T @ cov0_inv @ ct @ cov0_inv)
         if adjusted:
              to_add /= (nobs - t)
         statistic += to_add
    #statistic *= nobs**2 if adjusted else nobs
    if adjusted:
         statistic *= nobs**2
    else:
        statistic = nobs*statistic+nlags*(nlags+1)*K**2/(2*nobs)
    df = K**2 * nlags - noestimatedcoef
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

