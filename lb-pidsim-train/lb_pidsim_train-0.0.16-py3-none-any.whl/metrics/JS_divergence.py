#from __future__ import annotations

import numpy as np
from lb_pidsim_train.utils import getBinPDFs


def JS_divergence ( x_gen , 
                    x_ref , 
                    bins  = 100  , 
                    w_gen = None , 
                    w_ref = None ) -> np.ndarray:
  """Return the Jensen–Shannon divergence of the two input datasets.

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
  js_divergence : `np.ndarray`
    Array containing the J-S divergence for each feature of the two input datasets.

  See Also
  --------
  lb_pidsim_train.utils.getBinPDFs : 
    Internal function used to compute the binned PDFs of the input datasets.

  lb_pidsim_train.metrics.KL_divergence : 
    The Jensen–Shannon divergence is a symmetrized and smoothed version of 
    the Kullback–Leibler divergence.

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
  :math:`D_{KL} (P \parallel Q)`. It is defined by

  .. math::

    D_{JS} (P \parallel Q) = \frac{1}{2} D_{KL} (P \parallel M) + \frac{1}{2} D_{KL} (Q \parallel M),
  
  where :math:`M = \frac{1}{2} (P + Q)`.

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
  >>> from lb_pidsim_train.metrics import JS_divergence
  >>> JS_divergence ( a, b )
  [0.04374737]
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

  ## J-S divergence computation
  m = 0.5 * (p + q)

  kl_pm = np.sum ( p * np.log2 (p / m), axis = 1 )   # KL(p||m)
  kl_qm = np.sum ( q * np.log2 (q / m), axis = 1 )   # KL(q||m)

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
    js_div = JS_divergence (sample_1, sample_2, bins)
    print ( "J-S divergence (bins - {:.2e}) : {}" . format (bins, js_div) )
