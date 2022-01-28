import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def  qstatf(x, type="LjungBox", noestimatedcoef=0, nolags=1):
        
    """
    x : Series-like
         Series to be analyzed or residuals to be tested when modeling.
    noestimatedcoef: int
        Number of estimated coefficients when modeling.   
     nolags: int
        Max number of added terms in LB statistic.  nolags > noestimatedcoef
     
    Returns
    -------
    q-stat : array
        Ljung-Box Q-statistic for autocorrelation parameters
    p-value : array
        P-value of the Q statistic

    """
    avf =acovf(x, unbiased=False, demean=True, fft=False, missing='none')
    acf = avf[:nolags + 1] / avf[0]
    y=acf[1:]
    nobs=len(x)
    if type == "LjungBox":
        lb = (nobs * (nobs + 2) * np.cumsum((1. / (nobs - np.arange(1, len(y) + 1))) * y**2))
    if noestimatedcoef==0:   
       pvalue = stats.chi2.sf(lb, np.arange(1, len(y)+1 ))
    else:
       p= np.arange(1, len(y) + 1)
       pvalue=np.array(p,dtype='float')
       for i in  np.arange(1, len(y) + 1):
             if i>noestimatedcoef:
                pvalue[i-1] = stats.chi2.sf(lb[i-1], i-noestimatedcoef)
             else:
                 pvalue[i-1]=None

        
    return lb[noestimatedcoef:], pvalue[noestimatedcoef:]


def acovf(x, unbiased=False, demean=True, fft=False, missing='none'):
     x = np.squeeze(np.asarray(x))
     if x.ndim > 1:
        raise ValueError("x must be 1d. Got %d dims." % x.ndim)

     missing = missing.lower()
     if missing not in ['none', 'raise', 'conservative', 'drop']:
        raise ValueError("missing option %s not understood" % missing)
     if missing == 'none':
        deal_with_masked = False
     else:
        deal_with_masked = has_missing(x)
     if deal_with_masked:
        if missing == 'raise':
            raise MissingDataError("NaNs were encountered in the data")
        notmask_bool = ~np.isnan(x) #bool
        if missing == 'conservative':
            x[~notmask_bool] = 0
        else: #'drop'
            x = x[notmask_bool] #copies non-missing
        notmask_int = notmask_bool.astype(int) #int

     if demean and deal_with_masked:
        # whether 'drop' or 'conservative':
        xo = x - x.sum()/notmask_int.sum()
        if missing=='conservative':
            xo[~notmask_bool] = 0
     elif demean:
         xo = x - x.mean()
     else:
        xo = x

     n = len(x)
     if unbiased and deal_with_masked and missing=='conservative':
        d = np.correlate(notmask_int, notmask_int, 'full')
     elif unbiased:
         xi = np.arange(1, n + 1)
         d = np.hstack((xi, xi[:-1][::-1]))
     elif deal_with_masked: #biased and NaNs given and ('drop' or 'conservative')
         d = notmask_int.sum() * np.ones(2*n-1)
     else: #biased and no NaNs or missing=='none'
         d = n * np.ones(2 * n - 1)

     if fft:
        nobs = len(xo)
        n = _next_regular(2 * nobs + 1)
        Frf = np.fft.fft(xo, n=n)
        acov = np.fft.ifft(Frf * np.conjugate(Frf))[:nobs] / d[nobs - 1:]
        acov = acov.real
     else:
        acov = (np.correlate(xo, xo, 'full') / d)[n - 1:]

     if deal_with_masked and missing=='conservative':
        # restore data for the user
        x[~notmask_bool] = np.nan

     return acov


def  plot_LB_pvalue(x, noestimatedcoef, nolags):
      LB, pv=qstatf(x, noestimatedcoef, nolags, type="LjungBox")
      Lag=range(noestimatedcoef+1, nolags+1)
      from matplotlib.ticker import MultipleLocator
      xmajorLocator = MultipleLocator(1)
      ticks=range(noestimatedcoef+1, nolags+1, 2)
      fig = plt.figure()
      ax =fig.add_subplot(111)
      ax.xaxis.set_major_locator(xmajorLocator)
      plt.plot(Lag, pv, linestyle='', marker='.')
      plt.xlabel('Lag')
      plt.ylabel('p-value')
      plt.axhline(y=0.05, linestyle=':', color='b')
      plt.title('p-values for Ljung-Box statistic')
      plt.xticks(ticks=ticks)
      plt.show()
      
      
       
def  qstatf(x, noestimatedcoef, nolags, type="LjungBox"):
    """
    x : Series-like
         Series to be analyzed or residuals to be tested when modeling.
    noestimatedcoef: int
        Number of estimated coefficients when modeling.   
     nolags: int
        Max number of added terms in LB statistic.  nolags > noestimatedcoef
     
    Returns
    -------
    q-stat : array
        Ljung-Box Q-statistic for autocorrelation parameters
    p-value : array
        P-value of the Q statistic

    """
    avf =acovf(x, unbiased=False, demean=True, fft=False, missing='none')
    acf = avf[:nolags + 1] / avf[0]
    y=acf[1:]
    nobs=len(x)
    if type == "LjungBox":
        lb = (nobs * (nobs + 2) * np.cumsum((1. / (nobs - np.arange(1, len(y) + 1))) * y**2))
    if noestimatedcoef==0:   
       pvalue = stats.chi2.sf(lb, np.arange(1, len(y)+1 ))
    else:
       p= np.arange(1, len(y) + 1)
       pvalue=np.array(p,dtype='float')
       for i in  np.arange(1, len(y) + 1):
             if i>noestimatedcoef:
                pvalue[i-1] = stats.chi2.sf(lb[i-1], i-noestimatedcoef)
             else:
                 pvalue[i-1]=None

        
    return lb[noestimatedcoef:], pvalue[noestimatedcoef:]




