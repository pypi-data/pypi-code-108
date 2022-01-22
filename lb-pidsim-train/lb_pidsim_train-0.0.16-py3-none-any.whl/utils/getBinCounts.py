#from __future__ import annotations

import numpy as np


def getBinCounts ( x_obs , 
                   x_exp , 
                   bins  = 100  ,
                   w_obs = None , 
                   w_exp = None ) -> tuple:
  """Return the bin counts of the two input datasets.

  Parameters
  ----------
  x_obs : array_like
    Array containing the observed dataset.

  x_exp : array_like
    Array containing the expected dataset.

  bins : `int`, optional
    Number of equal-width bins in the computed range used to approximate 
    the two distributions with binned data (`100`, by default).

  w_obs : `int` or `float` or array_like, optional
    An array of weights, of the same length as `x_obs`. Each value in `x_obs` 
    only contributes its associated weight towards the bin count (instead of 1).

  w_exp : `int` or `float` or array_like, optional
    An array of weights, of the same length as `x_exp`. Each value in `x_exp` 
    only contributes its associated weight towards the bin count (instead of 1).

  Returns
  -------
  n_obs : `np.ndarray`
    Bin counts of the observed dataset.

  n_exp : `np.ndarray`
    Bin counts of the expected dataset.

  See Also
  --------
  numpy.histogram :
    Numpy function used to compute the bin counts of the input datasets.

  lb_pidsim_train.metrics.KL_div : 
    The bin counts are used to compute the Kullback–Leibler divergence.

  lb_pidsim_train.metrics.JS_div : 
    The bin counts are used to compute the Jensen-Shannon divergence.

  lb_pidsim_train.metrics.KS_test : 
    The bin counts are used to perform the Kolmogorov–Smirnov test.

  lb_pidsim_train.metrics.chi2_test : 
    The bin counts are used to perform the chi-squared test.
  """
  ## Input samples --> Numpy arrays
  x_obs = np.array ( x_obs )
  x_exp = np.array ( x_exp )

  ## Promotion to 2-D arrays
  if len (x_obs.shape) == 1:
    x_obs = x_obs [:, np.newaxis]
  if len (x_exp.shape) == 1:
    x_exp = x_exp [:, np.newaxis]

  ## Dimension control
  if x_obs.shape[1] != x_exp.shape[1]:
    raise ValueError ("The two samples should have the same number of features.")

  ## Data-type control
  try:
    bins = int ( bins )
  except:
    raise TypeError ("The number of bins should be an integer.")

  ## Default weights
  if w_obs is None: w_obs = 1.
  if w_exp is None: w_exp = 1.

  ## Scalar weights --> vector weights
  if isinstance ( w_obs, (int, float) ):
    w_obs = w_obs * np.ones ( len(x_obs) )
  if isinstance ( w_exp, (int, float) ):
    w_exp = w_exp * np.ones ( len(x_exp) )

  ## Input weights --> Numpy arrays
  w_obs = np.array ( w_obs )
  w_exp = np.array ( w_exp )

  ## Binned PDFs computation
  n_obs, n_exp = list(), list()  
  for i in range (x_obs.shape[1]):  # loop over features
    minval = min ( min(x_obs[:,i]), min(x_exp[:,i]) )
    maxval = max ( max(x_obs[:,i]), max(x_exp[:,i]) )

    h_obs, _ = np.histogram ( x_obs[:,i], 
                              bins = bins, range = [minval, maxval], 
                              weights = w_obs / len(x_obs[:,i]) )
    h_exp, _ = np.histogram ( x_exp[:,i], 
                              bins = bins, range = [minval, maxval], 
                              weights = w_exp / len(x_exp[:,i]) )
    n_obs . append ( h_obs )
    n_exp . append ( h_exp )
  
  return np.array(n_obs), np.array(n_exp)



if __name__ == "__main__":
  ## SAMPLE N. 1
  gauss_1 = np.random.normal  ( 0.   , 1.  , size = int(1e6) )
  unif_1  = np.random.uniform ( -0.5 , 0.5 , size = int(1e6) )
  sample_1 = np.c_ [gauss_1, unif_1]

  ## SAMPLE N. 2
  gauss_2 = np.random.normal  ( 0.5  , 1.  , size = int(1e6) )
  unif_2  = np.random.uniform ( -0.4 , 0.6 , size = int(1e6) )
  sample_2 = np.c_ [gauss_2, unif_2]

  pdf_1, pdf_2 = getBinCounts (sample_1, sample_2)
  print ( "PDF1 - sum:", np.sum (pdf_1, axis = 1) )
  print ( "PDF2 - sum:", np.sum (pdf_2, axis = 1) )
