#from __future__ import annotations

import numpy as np
from lb_pidsim_train.utils import getBinPDFs


def KL_divergence ( x_gen , 
                    x_ref , 
                    bins  = 100  , 
                    w_gen = None , 
                    w_ref = None ) -> np.ndarray:
  """Return the Kullback–Leibler divergence of the two input datasets.

  Parameters
  ----------
  x_gen : array_like
    Array containing the generated dataset.

  x_ref : array_like
    Array containing the reference dataset.

  bins : `int`, optional
    Number of equal-width bins in the computed range used to approximate 
    the two PDFs with binned data (`100`, by default).

  w_gen : `int` or `float` or array_like, optional
    An array of weights, of the same length as `x_gen`. Each value in `x_gen` 
    only contributes its associated weight towards the bin count (instead of 1).

  w_ref : `int` or `float` or array_like, optional
    An array of weights, of the same length as `x_ref`. Each value in `x_ref` 
    only contributes its associated weight towards the bin count (instead of 1).

  Returns
  -------
  kl_divergence : `np.ndarray`
    Array containing the K-L divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.utils.getBinPDFs : 
    Internal function used to compute the binned PDFs of the input datasets.

  lb_pidsim_train.metrics.JS_divergence : 
    The Jensen–Shannon divergence is a symmetrized and smoothed version of 
    the Kullback–Leibler divergence.

  Notes
  -----
  In mathematical statistics, the **Kullback–Leibler divergence**, :math:`D_{KL}` 
  (also called **relative entropy**), is a measure of how one probability distribution 
  is different from a second, reference probability distribution [1]_ [2]_.

  For discrete probability distributions :math:`P` and :math:`Q` defined on the same 
  *probability space*, :math:`\mathcal{X}`, the relative entropy from :math:`Q` to 
  :math:`P` is defined [3]_ to be

  .. math::

     D_{KL} (P \parallel Q) = \sum_{x \in \mathcal{X}} P(x) \log \left ( \frac{P(x)}{Q(x)} \right ).

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
  >>> from lb_pidsim_train.metrics import KL_divergence
  >>> KL_divergence ( a, b )
  [0.1805024]
  """
  ## Binned PDFs
  p , q = getBinPDFs (x_gen, x_ref, bins, w_gen, w_ref)

  ## Promotion to 2-D arrays
  if len (p.shape) == 1:
    p = p [:, np.newaxis]
  if len (q.shape) == 1:
    q = q [:, np.newaxis]

  ## Cleaning datasets from 0s
  p = np.where (p > 0, p, 1e-12)
  q = np.where (q > 0, q, 1e-12)

  ## K-L divergence computation
  return np.sum ( p * np.log2 (p / q), axis = 1 )



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
    kl_div = KL_divergence (sample_1, sample_2, bins)
    print ( "K-L divergence (bins - {:.2e}) : {}" . format (bins, kl_div) )
  