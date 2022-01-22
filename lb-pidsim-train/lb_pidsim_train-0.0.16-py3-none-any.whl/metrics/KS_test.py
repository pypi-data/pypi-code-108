#from __future__ import annotations

import numpy as np
from lb_pidsim_train.utils import getBinCounts


def KS_test ( x_obs , 
              x_exp , 
              bins  = 100  , 
              w_obs = None , 
              w_exp = None ) -> np.ndarray:
  """Return the Kolmogorov–Smirnov test of the two input datasets.

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
  ks_test : `np.ndarray`
    Array containing the K-S test for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.utils.getBinCounts : 
    Internal function used to compute the bin counts of the input datasets.

  lb_pidsim_train.metrics.KS_test_from_counts :
    Function used to compute the K-S test of two datasets from bin counts.

  Notes
  -----
  In statistics, the **Kolmogorov–Smirnov test** (K–S test) is a nonparametric 
  test of the equality of one-dimensional probability distributions that can be 
  used to compare two samples.

  Let :math:`F(x)` be the cumulative distribution function of the observed
  dataset and :math:`G(x)` be the one of the expected dataset, then the
  Kolmogorov-Smirnov statistic is 

  .. math::

    D_{KS} = \sup_{x} \left | F(x) - G(x) \right |,

  where :math:`\sup` is the supremum function.

  Examples
  --------
  >>> import numpy as np
  >>> a = np.random.normal ( 0. , 1., 10000 )
  >>> b = np.random.normal ( 0.5, 1., 10000 )
  >>> from lb_pidsim_train.metrics import KS_test
  >>> KS_test ( a, b )
  [0.197325]
  """
  n_obs , n_exp = getBinCounts (x_obs, x_exp, bins, w_obs, w_exp)
  return KS_test_from_counts (n_obs, n_exp)


def KS_test_from_counts (f, g):
  """Return the Kolmogorov–Smirnov test of the two input datasets from bin counts.

  Parameters
  ----------
  f : array_like
    Array containing the bin counts of the observed dataset.

  g : array_like
    Array containing the bin counts of the expected dataset.

  Returns
  -------
  ks_test : `np.ndarray`
    Array containing the K-S test for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.metrics.KS_test :
    Function used to compute the K-S test of two datasets.

  Notes
  -----
  In statistics, the **Kolmogorov–Smirnov test** (K–S test) is a nonparametric 
  test of the equality of one-dimensional probability distributions that can be 
  used to compare two samples.

  Let :math:`F(x)` be the cumulative distribution function of the observed
  dataset and :math:`G(x)` be the one of the expected dataset, then the
  Kolmogorov-Smirnov statistic is 

  .. math::

    D_{KS} = \sup_{x} \left | F(x) - G(x) \right |,

  where :math:`\sup` is the supremum function.

  Examples
  --------
  >>> import numpy as np
  >>> a = [15, 33, 59, 93, 101, 85, 68, 42, 18, 5]
  >>> b = [10, 45, 67, 104, 92, 93, 55, 31, 27, 2]
  >>> from lb_pidsim_train.metrics import KS_test_from_counts
  >>> KS_test_from_counts ( a, b )
  [0.04430134]
  """
  ## Input samples --> Numpy arrays
  f = np.array (f)
  g = np.array (g)

  ## Promotion to 2-D arrays
  if len (f.shape) == 1:
    f = f [np.newaxis,:]
  if len (g.shape) == 1:
    g = g [np.newaxis,:]

  ## Normalize distributions
  cdf_f = np.cumsum (f, axis = 1)[:,-1]
  cdf_f = np.where (cdf_f > 0, cdf_f, 1)
  f = f / cdf_f[:,np.newaxis]

  cdf_g = np.cumsum (g, axis = 1)[:,-1]
  cdf_g = np.where (cdf_g > 0, cdf_g, 1)
  g = g / cdf_g[:,np.newaxis]

  ## CDFs computation
  F = np.cumsum (f, axis = 1)
  G = np.cumsum (g, axis = 1)

  ## K-S test computation
  return np.absolute (F - G) . max (axis = 1)



if __name__ == "__main__":
  ## SAMPLE N. 1
  gauss_1 = np.random.normal  ( 0.   , 1.  , size = int(1e6) )
  unif_1  = np.random.uniform ( -0.5 , 0.5 , size = int(1e6) )
  sample_1 = np.c_ [gauss_1, unif_1]

  ## SAMPLE N. 2
  gauss_2 = np.random.normal  ( 0.5  , 1.  , size = int(1e6) )
  unif_2  = np.random.uniform ( -0.4 , 0.6 , size = int(1e6) )
  sample_2 = np.c_ [gauss_2, unif_2]

  binnings = [10, 100, 1000, 10000]
  for bins in binnings:
    ks_test = KS_test (sample_1, sample_2, bins)
    print ( "K-S test (bins - {:.2e}) : {}" . format (bins, ks_test) )
  