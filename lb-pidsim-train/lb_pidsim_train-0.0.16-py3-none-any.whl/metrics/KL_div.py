#from __future__ import annotations

import numpy as np
from lb_pidsim_train.utils import getBinCounts


def KL_div ( x_obs , 
             x_exp , 
             bins  = 100  , 
             w_obs = None , 
             w_exp = None ) -> np.ndarray:
  """Return the Kullback–Leibler divergence of the two input datasets.

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
  kl_div : `np.ndarray`
    Array containing the K-L divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.utils.getBinCounts : 
    Internal function used to compute the bin counts of the input datasets.

  lb_pidsim_train.metrics.KL_div_from_counts : 
    Function used to compute the K-L divergence of two datasets from bin counts.

  Notes
  -----
  In mathematical statistics, the **Kullback–Leibler divergence**, :math:`D_{KL}` 
  (also called **relative entropy**), is a measure of how one probability distribution 
  is different from a second, reference probability distribution [1]_ [2]_.

  For discrete probability distributions :math:`F` and :math:`G` defined on the same 
  *probability space*, :math:`\mathcal{X}`, the relative entropy from :math:`G` to 
  :math:`F` is defined [3]_ to be

  .. math::

     D_{KL} (F \parallel G) = \sum_{x \in \mathcal{X}} F(x) \log \left ( \frac{F(x)}{G(x)} \right ).

  References
  ----------
  .. [1] S. Kullback and R.A. Leibler, "On Information and Sufficiency", The Annals 
     of Mathematical Statistics **22** (1951) 1.

  .. [2] S. Kullback, "Information Theory and Statistics", Wiley, New York, 1959.

  .. [3] D.J.C. MacKay, "Information Theory, Inference & Learning Algorithms",
     Cambridge University Press, Cambridge, 2002.

  Examples
  --------
  >>> import numpy as np
  >>> a = np.random.normal ( 0. , 1., 10000 )
  >>> b = np.random.normal ( 0.5, 1., 10000 )
  >>> from lb_pidsim_train.metrics import KL_div
  >>> KL_divergence ( a, b )
  [0.18010471]
  """
  n_obs , n_exp = getBinCounts (x_obs, x_exp, bins, w_obs, w_exp)
  return KL_div_from_counts (n_obs, n_exp)


def KL_div_from_counts (f, g):
  """Return the Kullback–Leibler divergence of the two input datasets from bin counts.

  Parameters
  ----------
  f : array_like
    Array containing the bin counts of the observed dataset.

  g : array_like
    Array containing the bin counts of the expected dataset.

  Returns
  -------
  kl_div : `np.ndarray`
    Array containing the K-L divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.metrics.KL_div :
    Function used to compute the K-L divergence of two datasets.

  Notes
  -----
  In mathematical statistics, the **Kullback–Leibler divergence**, :math:`D_{KL}` 
  (also called **relative entropy**), is a measure of how one probability distribution 
  is different from a second, reference probability distribution [1]_ [2]_.

  For discrete probability distributions :math:`F` and :math:`G` defined on the same 
  *probability space*, :math:`\mathcal{X}`, the relative entropy from :math:`G` to 
  :math:`F` is defined [3]_ to be

  .. math::

     D_{KL} (F \parallel G) = \sum_{x \in \mathcal{X}} F(x) \log \left ( \frac{F(x)}{G(x)} \right ).

  References
  ----------
  .. [1] S. Kullback and R.A. Leibler, "On Information and Sufficiency", The Annals 
     of Mathematical Statistics **22** (1951) 1.

  .. [2] S. Kullback, "Information Theory and Statistics", Wiley, New York, 1959.

  .. [3] D.J.C. MacKay, "Information Theory, Inference & Learning Algorithms",
     Cambridge University Press, Cambridge, 2002.

  Examples
  --------
  >>> import numpy as np
  >>> a = [15, 33, 59, 93, 101, 85, 68, 42, 18, 5]
  >>> b = [10, 45, 67, 104, 92, 93, 55, 31, 27, 2]
  >>> from lb_pidsim_train.metrics import KL_div_from_counts
  >>> KL_div_from_counts ( a, b )
  [0.03098836]
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

  ## Cleaning datasets from 0s
  f = np.where (f > 0, f, 1e-12)
  g = np.where (g > 0, g, 1e-12)

  ## K-L divergence computation
  return np.sum ( f * np.log2 (f / g), axis = 1 )



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
    kl_div = KL_div (sample_1, sample_2, bins)
    print ( "K-L divergence (bins - {:.2e}) : {}" . format (bins, kl_div) )
  