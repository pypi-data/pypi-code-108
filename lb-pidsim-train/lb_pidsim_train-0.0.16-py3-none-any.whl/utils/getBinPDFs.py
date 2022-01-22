#from __future__ import annotations

import numpy as np


def getBinPDFs ( x_gen , 
                 x_ref , 
                 bins  = 100  ,
                 w_gen = None , 
                 w_ref = None ) -> tuple:
  """Return two binned PDFs for the two input datasets.

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
  pdf_gen : `np.ndarray`
    Binned PDF for the generated dataset.

  pdf_ref : `np.ndarray`
    Binned PDF for the reference dataset.

  See Also
  --------
  numpy.histogram :
    Numpy function used to compute the binned PDFs of the input datasets.

  lb_pidsim_train.metrics.KL_divergence : 
    The binned PDFs are used to compute the Kullback–Leibler divergence.

  lb_pidsim_train.metrics.JS_divergence : 
    The binned PDFs are used to compute the Jensen-Shannon divergence.

  lb_pidsim_train.metrics.KS_test : 
    The binned PDFs are used to perform the Kolmogorov–Smirnov test.
  """
  ## Input samples --> Numpy arrays
  x_gen = np.array ( x_gen )
  x_ref = np.array ( x_ref )

  ## Promotion to 2-D arrays
  if len (x_gen.shape) == 1:
    x_gen = x_gen [:, np.newaxis]
  if len (x_ref.shape) == 1:
    x_ref = x_ref [:, np.newaxis]

  ## Dimension control
  if x_gen.shape[1] != x_ref.shape[1]:
    raise ValueError ("The two samples should have the same number of features.")

  ## Data-type control
  try:
    bins = int ( bins )
  except:
    raise TypeError ("The number of bins should be an integer.")

  ## Default weights
  if w_gen is None: w_gen = 1.
  if w_ref is None: w_ref = 1.

  ## Scalar weights --> vector weights
  if isinstance ( w_gen, (int, float) ):
    w_gen = w_gen * np.ones ( len(x_gen) )
  if isinstance ( w_ref, (int, float) ):
    w_ref = w_ref * np.ones ( len(x_ref) )

  ## Input weights --> Numpy arrays
  w_gen = np.array ( w_gen )
  w_ref = np.array ( w_ref )

  ## Binned PDFs computation
  pdf_gen, pdf_ref = list(), list()  
  for i in range (x_gen.shape[1]):  # loop over features
    minval = min ( min(x_gen[:,i]), min(x_ref[:,i]) )
    maxval = max ( max(x_gen[:,i]), max(x_ref[:,i]) )

    hist_gen, _ = np.histogram ( x_gen[:,i], 
                                 bins = bins, range = [minval, maxval], 
                                 weights = w_gen / len(x_gen[:,i]) )
    hist_ref, _ = np.histogram ( x_ref[:,i], 
                                 bins = bins, range = [minval, maxval], 
                                 weights = w_ref / len(x_ref[:,i]) )
    pdf_gen . append ( hist_gen )
    pdf_ref . append ( hist_ref )
  
  return np.array(pdf_gen), np.array(pdf_ref)



if __name__ == "__main__":
  ## SAMPLE N. 1
  gauss_1 = np.random.normal  ( 0.   , 1.  , size = int(1e6) )
  unif_1  = np.random.uniform ( -0.5 , 0.5 , size = int(1e6) )
  sample_1 = np.c_ [gauss_1, unif_1]

  ## SAMPLE N. 2
  gauss_2 = np.random.normal  ( 0.5  , 1.  , size = int(1e6) )
  unif_2  = np.random.uniform ( -0.4 , 0.6 , size = int(1e6) )
  sample_2 = np.c_ [gauss_2, unif_2]

  pdf_1, pdf_2 = getBinPDFs (sample_1, sample_2)
  print ( "PDF1 - sum:", np.sum (pdf_1, axis = 1) )
  print ( "PDF2 - sum:", np.sum (pdf_2, axis = 1) )
