#from __future__ import annotations

import numpy as np


def nan_filter (x, when_nan = 0.) -> np.ndarray:
  """Replace NaN elements within `x` with the `when_nan` value.

  Parameters
  ----------
    x : array_like
      Array from which to remove NaN elements.

    when_nan : `float`, optional
      Value with which to replace NaN elements within `x` (`0.`, by default).

  Returns
  -------
    x_filtered : array_like
      An array with NaN elements replaced by the `when_nan` value.

  Examples
  --------
  >>> import numpy as np
  >>> nan_arr = np.ones (5)
  >>> nan_arr[1:] = np.NaN
  >>> print (nan_arr)
  [ 1. nan nan nan nan]
  >>> from lb_pidsim_train.utils import nan_filter
  >>> filt_arr = nan_filter (nan_arr)
  >>> print (filt_arr)
  [1. 0. 0. 0. 0.]
  """
  ## Input array --> Numpy array
  x = np.array (x) . astype (np.float64)

  ## Data-type control
  try:
    when_nan = float (when_nan)
  except:
    raise TypeError ("The value replacing NaN elements should be a float.")

  ## Filter application
  x_finite = np.isfinite (x)
  x_nan = np.full_like (x, when_nan)
  x_filtered = np.where (x_finite, x, x_nan)
  return x_filtered



if __name__ == "__main__":
  ## NaN array
  nan_arr = np.ones (5)
  nan_arr[1:] = np.NaN
  print (nan_arr)

  ## Filtered array
  filt_arr = nan_filter (nan_arr)
  print (filt_arr)