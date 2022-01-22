#from __future__ import annotations

import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler, QuantileTransformer, FunctionTransformer
from lb_pidsim_train.utils import PidsimColTransformer


def preprocessor ( data ,
                   strategy = "quantile" , 
                   cols_to_transform = None ) -> PidsimColTransformer:
  """Scikit-Learn transformer for data preprocessing.
  
  Parameters
  ----------
  data : `np.ndarray`
    Array to preprocess according to a specific strategy.

  strategy : {'quantile', 'standard', 'minmax'}, optional
    Strategy to use for preprocessing (`'quantile'`, by default).
    The `'quantile'` strategy relies on the Scikit-Learn's 
    `QuantileTransformer`, `'standard'` implements `StandardScaler`,
    while `'minmax'` stands for `MinMaxScaler`.

  cols_to_transform : `list` of `int` or `np.ndarray`, optional
    Indices of the data columns to which apply the preprocessing 
    transformation (`None`, by default). If `None` is selected, 
    all the data columns are preprocessed.

  Returns
  -------
  scaler : `lb_pidsim_train.utils.PidsimColTransformer`
    Scikit-Learn transformer fitted and ready to use (calling the 
    `transform` method).

  See Also
  --------
  sklearn.preprocessing.QuantileTransformer :
    Transform features using quantiles information.

  sklearn.preprocessing.StandardScaler :
    Standardize features by removing the mean and scaling to unit variance.

  sklearn.preprocessing.MinMaxScaler :
    Transform features by scaling each feature to a given range.

  Examples
  --------
  >>> import numpy as np
  >>> a = np.random.uniform (-5, 5, 1000)
  >>> b = np.random.exponential (2, 1000)
  >>> c = np.where (a < 0, -1, 1)
  >>> data = np.c_ [a, b, c]
  >>> print (data)
  [[-3.49523994  3.15785198 -1.        ]
   [-3.98305793  4.76562602 -1.        ]
   [-3.06980643  0.23196773 -1.        ]
   ...
   [-4.43405151  0.45379785 -1.        ]
   [ 2.91133207  0.18502709  1.        ]
   [-0.13924445  2.01237511 -1.        ]]
  >>> from lb_pidsim_train.utils import preprocessor
  >>> scaler = preprocessor (data, "quantile", [0,1])
  >>> data_scaled = scaler . transform (data)
  >>> print (data_scaled)
  [[-1.04874761  0.87719565 -1.        ]
   [-1.35262276  1.33406614 -1.        ]
   [-0.89577982 -1.24750548 -1.        ]
   ...
   [-1.67418578 -0.83023416 -1.        ]
   [ 0.7987689  -1.35891295  1.        ]
   [-0.05648561  0.32822342 -1.        ]]
  >>> data_inv_tr = scaler . inverse_transform (data_scaled)
  >>> print (data_inv_tr)
  [[-3.49523994  3.15785198 -1.        ]
   [-3.98305793  4.76562602 -1.        ]
   [-3.06980643  0.23196773 -1.        ]
   ...
   [-4.43405151  0.45379785 -1.        ]
   [ 2.91133207  0.18502709  1.        ]
   [-0.13924445  2.01237511 -1.        ]]
  """
  ## Strategy selection
  if strategy == "minmax":
    num_scaler = MinMaxScaler()
  elif strategy == "standard":
    num_scaler = StandardScaler()
  elif strategy == "quantile":
    num_scaler = QuantileTransformer ( output_distribution = "normal" )
  else:
    raise ValueError ( f"Preprocessing strategy not implemented. Available strategies " 
                       f"are ['quantile', 'standard', 'minmax'], '{strategy}' passed." )

  ## Default column indices
  all_cols = np.arange (data.shape[1]) . astype (np.int32)
  if cols_to_transform is not None:
    cols_to_transform = list ( cols_to_transform )
    if len(cols_to_transform) != 0:
      cols_to_ignore = list ( np.delete (all_cols, cols_to_transform) )
    else:
      cols_to_ignore = list ( all_cols )
  else:
    cols_to_transform = list ( all_cols )
    cols_to_ignore = []

  scaler = PidsimColTransformer ( [
                                    ( "num", num_scaler, cols_to_transform ) ,
                                    ( "cls", FunctionTransformer(), cols_to_ignore )
                                  ] )
  
  scaler . fit ( data )
  return scaler



if __name__ == "__main__":
  ## Dataset
  a = np.random.uniform (-5, 5, 1000)
  b = np.random.exponential (2, 1000)
  c = np.where (a < 0, -1, 1)
  data = np.c_ [a, b, c]
  print (data)

  ## Dataset after preprocessing
  scaler = preprocessor (data, "quantile", [0,1])
  data_scaled = scaler . transform (data)
  print (data_scaled)

  ## Dataset back-projected
  data_inv_tr = scaler . inverse_transform (data_scaled)
  print (data_inv_tr)
