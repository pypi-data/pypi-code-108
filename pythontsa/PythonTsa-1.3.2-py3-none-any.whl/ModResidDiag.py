import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from statsmodels.graphics.api import qqplot
from statsmodels.tsa.stattools import acf

def  plot_ResidDiag(x, noestimatedcoef, nolags,  lag=30):
      
      """
      x : Series-like
         Series to be analyzed or residuals to be diagnosed when modeling.
      noestimatedcoef: int
         Number of estimated coefficients when modeling.   
      nolags: int
         Max number of added terms in LB statistic.  nolags > noestimatedcoef
      lag: int
         Number of lags for ACF of x and squared x
        
      """
      LB, pv=qstatf(x, noestimatedcoef, nolags, type="LjungBox")
      Lag=range(noestimatedcoef+1, nolags+1)
      from matplotlib.ticker import MultipleLocator
      xmajorLocator = MultipleLocator(1)
      fig=plt.figure(figsize=(9,13))
      ax1 =fig.add_subplot(411)
      ax1.xaxis.set_major_locator(xmajorLocator)
      ax1.plot(Lag, pv, linestyle='', marker='.')
      plt.xlabel('Lag')
      plt.ylabel('p-value')
      plt.axhline(y=0.05, linestyle=':', color='b')
      plt.title('p-values for Ljung-Box statistic')
      ax2 = fig.add_subplot(412)
      qqplot(x, line='q', fit=True, ax=ax2)
      if lag<31:
           ticks=range(lag+1)
      else:
           ticks=range(0, lag+1, 5)
      plt.subplot(413)
      acf_lag=acf(x, nlags=lag, fft=False)
      plt.vlines(range(lag+1), [0], acf_lag)
      plt.axhline(y=0.0,linewidth=1)
      plt.axhline(y=1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
      plt.axhline(y=-1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
      plt.xticks(ticks=ticks)
      plt.ylabel('ACF of Resid')
      plt.subplot(414)
      rres=x**2
      acf_lag=acf(rres, nlags=lag, fft=False)
      plt.vlines(range(lag+1), [0], acf_lag)
      plt.axhline(y=0.0,linewidth=1)
      plt.axhline(y=1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
      plt.axhline(y=-1.96/np.sqrt(len(x)),  linestyle='--', color='blue', linewidth=1)
      plt.xticks(ticks=ticks)
      plt.xlabel('Lag')
      plt.ylabel('ACF of Sq Resid')
      plt.show()
      
def  qstatf(x, noestimatedcoef, nolags, type):
        
    """
    Returns
    -------
    lb : array
        Ljung-Box Q-statistic for autocorrelation 
    pvalue : array
        P-value of the LB statistic

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


