#from __future__ import annotations

import numpy as np
from lb_pidsim_train.utils import getBinCounts


def JS_div ( x_obs , 
             x_exp , 
             bins  = 100  , 
             w_obs = None , 
             w_exp = None ) -> np.ndarray:
  """Return the Jensen–Shannon divergence of the two input datasets.

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
  js_divergence : `np.ndarray`
    Array containing the J-S divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.utils.getBinCounts : 
    Internal function used to compute the bin counts of the input datasets.

  lb_pidsim_train.metrics.JS_div_from_counts : 
    Function used to compute the J-S divergence of two datasets from bin counts.

  Notes
  -----
  In probability theory and statistics, the **Jensen–Shannon divergence** is 
  a method of measuring the similarity between two probability distributions. 
  It is also known as **information radius** (IRad) [1]_ or **total divergence 
  to the average** [2]_.

  Consider the set :math:`M_{+}^{1}(A)` of probability distributions where 
  :math:`A` is a set provided with some :math:`\sigma`-algebra of measurable 
  subsets. In particular we can take :math:`A` to be a finite or countable 
  set with all subsets being measurable. The Jensen–Shannon divergence 
  :math:`D_{JS}: M_{+}^{1}(A) \times M_{+}^{1}(A) \to [0, \infty)` is 
  a symmetrized and smoothed version of the Kullback–Leibler divergence 
  :math:`D_{KL} (F \parallel G)`. It is defined by

  .. math::

    D_{JS} (F \parallel G) = \frac{1}{2} D_{KL} (F \parallel M) + \frac{1}{2} D_{KL} (G \parallel M),
  
  where :math:`M = \frac{1}{2} (F + G)`.

  References
  ----------
  .. [1] C.D. Manning and H. Schutze, "Foundations of Statistical Natural Language 
     Processing", MIT Press, Cambridge, 1999.

  .. [2] I. Dagan, L. Lee and F. Pereira, "Similarity-Based Methods For Word 
     Sense Disambiguation", in Proceedings of the Thirty-Fifth Annual Meeting 
     of the Association for Computational Linguistics and Eighth Conference of 
     the European Chapter of the Association for Computational Linguistics, 
     ACL-EACL 1997.

  Examples
  --------
  >>> import numpy as np
  >>> a = np.random.normal ( 0. , 1., 10000 )
  >>> b = np.random.normal ( 0.5, 1., 10000 )
  >>> from lb_pidsim_train.metrics import JS_div
  >>> JS_divergence ( a, b )
  [0.04380149]
  """
  n_obs , n_exp = getBinCounts (x_obs, x_exp, bins, w_obs, w_exp)
  return JS_div_from_counts (n_obs, n_exp)


def JS_div_from_counts (f, g):
  """Return the Jensen–Shannon divergence of the two input datasets from bin counts.

  Parameters
  ----------
  f : array_like
    Array containing the bin counts of the observed dataset.

  g : array_like
    Array containing the bin counts of the expected dataset.

  Returns
  -------
  js_div : `np.ndarray`
    Array containing the J-S divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.metrics.JS_div :
    Function used to compute the J-S divergence of two datasets.

  Notes
  -----
  In probability theory and statistics, the **Jensen–Shannon divergence** is 
  a method of measuring the similarity between two probability distributions. 
  It is also known as **information radius** (IRad) [1]_ or **total divergence 
  to the average** [2]_.

  Consider the set :math:`M_{+}^{1}(A)` of probability distributions where 
  :math:`A` is a set provided with some :math:`\sigma`-algebra of measurable 
  subsets. In particular we can take :math:`A` to be a finite or countable 
  set with all subsets being measurable. The Jensen–Shannon divergence 
  :math:`D_{JS}: M_{+}^{1}(A) \times M_{+}^{1}(A) \to [0, \infty)` is 
  a symmetrized and smoothed version of the Kullback–Leibler divergence 
  :math:`D_{KL} (F \parallel G)`. It is defined by

  .. math::

    D_{JS} (F \parallel G) = \frac{1}{2} D_{KL} (F \parallel M) + \frac{1}{2} D_{KL} (G \parallel M),
  
  where :math:`M = \frac{1}{2} (F + G)`.

  References
  ----------
  .. [1] C.D. Manning and H. Schutze, "Foundations of Statistical Natural Language 
     Processing", MIT Press, Cambridge, 1999.

  .. [2] I. Dagan, L. Lee and F. Pereira, "Similarity-Based Methods For Word 
     Sense Disambiguation", in Proceedings of the Thirty-Fifth Annual Meeting 
     of the Association for Computational Linguistics and Eighth Conference of 
     the European Chapter of the Association for Computational Linguistics, 
     ACL-EACL 1997.

  Examples
  --------
  >>> import numpy as np
  >>> a = [15, 33, 59, 93, 101, 85, 68, 42, 18, 5]
  >>> b = [10, 45, 67, 104, 92, 93, 55, 31, 27, 2]
  >>> from lb_pidsim_train.metrics import JS_div_from_counts
  >>> JS_div_from_counts ( a, b )
  [0.00752104]
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

  ## J-S divergence computation
  m = 0.5 * (f + g)

  kl_pm = np.sum ( f * np.log2 (f / m), axis = 1 )   # KL(f||m)
  kl_qm = np.sum ( g * np.log2 (g / m), axis = 1 )   # KL(g||m)

  return 0.5 * (kl_pm + kl_qm)



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
    js_div = JS_div (sample_1, sample_2, bins)
    print ( "J-S divergence (bins - {:.2e}) : {}" . format (bins, js_div) )
