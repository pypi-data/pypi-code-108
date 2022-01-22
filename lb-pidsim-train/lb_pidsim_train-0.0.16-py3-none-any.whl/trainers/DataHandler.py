#from __future__ import annotations

import uproot
import numpy as np
import pandas as pd

from time import time
from sklearn.utils import shuffle
from lb_pidsim_train.utils import data_from_trees, nan_filter


NP_FLOAT = np.float32
"""Default data-type for arrays."""


class DataHandler:   # TODO add class description
  """Handle the data-chunk for models training and assessing."""
  def __init__ (self) -> None:
    ## Switch off all flags
    self._datachunk_filled = False
    self._dataset_prepared = False

  def feed_from_root_files ( self ,
                             root_files  , 
                             X_vars = None , 
                             Y_vars = None ,
                             w_var  = None ,
                             selections = None ,
                             tree_names = None ,
                             chunk_size = None ,
                             verbose = 0 ) -> None:
    """Feed the training procedure with ROOT files.
    
    Parameters
    ----------
    root_files : `str` or `list` of `str`
      List of ROOT files used for the training procedure.

    X_vars : `str` or `list` of `str`, optional
      Branch names of the input variables within the ROOT trees
      (`None`, by default).

    Y_vars : `str` or `list` of `str`, optional
      Branch names of the output variables within the ROOT trees
      (`None`, by default).
    
    w_var : `str` or `list` of `str`, optional
      Branch name of the weight variable, if available, within the 
      ROOT trees (`None`, by default).

    selections : `str` or `list` of `str`, optional
      Boolean expressions to filter the ROOT trees (`None`, by default).

    tree_names : `str` or `list` of `str`, optional
      If more than one ROOT tree is defined for each file, the ones to 
      be loaded have to be defined specifying their names as the keys 
      (`None`, by default).

    chunk_size : `int` or `list` of `int`, optional
      Total number of instance rows loaded to disk for the training 
      procedure (`None`, by default).

    verbose : {0, 1}, optional
      Verbosity mode. `0` = silent (default), `1` = time for data-chunk 
      loading is printed. 

    See Also
    --------
    lb_pidsim_train.utils.data_from_trees :
      Stratified data shuffling from list of `uproot.TTree`.
    """
    ## List data-type promotion
    if isinstance (root_files, str):
      root_files = [root_files]
    if isinstance (X_vars, str):
      X_vars = [X_vars]
    if isinstance (Y_vars, str):
      Y_vars = [Y_vars]
    if isinstance (w_var, str):
      w_var = [w_var]
    if isinstance (selections, str):
      selections = [selections]
    if isinstance (tree_names, str):
      tree_names = [tree_names]

    self._X_vars = X_vars
    self._Y_vars = Y_vars
    self._w_var  = w_var

    ## List of branch names
    branches = list()
    if X_vars is not None:
      branches += X_vars
      if Y_vars is not None:
        branches += Y_vars
      if w_var is not None:
        branches += w_var
    else:
      branches = None

    ## Length match
    if tree_names is None:
      tree_names = [ None for i in range ( len(root_files) ) ]

    ## Check files and tree names match
    if len(root_files) != len(tree_names):
      raise ValueError ("The number of ROOT files should match with the tree names passed.")

    ## ROOT trees extraction
    trees = list()
    for fname, tname in zip (root_files, tree_names):
      file = uproot.open (fname)
      if tname is not None:
        key = tname
      else:
        key = file.keys()
        key = key[0] . split (";") [0]   # take the tree name
      t = file [key]
      trees . append (t)

    ## Data selection
    if selections:
      selections = "&".join ("(%s)" % s for s in selections)

    start = time()
    self._datachunk = data_from_trees ( trees = trees , 
                                        branches = branches ,
                                        cut = selections    ,
                                        chunk_size = chunk_size )
    self._datachunk_filled = True   # switch on datachunk-filled flag
    stop = time()
    if (verbose > 0): print ( f"Data-chunk of {len(self.datachunk)} rows"
                              f" correctly loaded in {stop-start:.3f} s" )

  def prepare_dataset (self, verbose = 0) -> None:
    """Split the data-chunk into X, Y and w.

    Parameters
    ----------
    verbose : `bool`, optional
      Verbosity mode. `False` = silent (default), 
      `True`= shuffling time is printed. 
    """
    if not self._datachunk_filled:
      raise RuntimeError ("error")   # TODO implement error

    X, Y, w = self._unpack_data()
    start = time()
    X, Y, w = shuffle (X, Y, w)
    stop = time()
    if verbose: print ( f"Shuffle-time: {stop-start:.3f} s" )

    self._X = X
    self._Y = Y
    self._w = w

    self._dataset_prepared = True   # switch on dataset prepared flag

  def _unpack_data (self) -> tuple:
    """Unpack the data-chunk into input, output and weights 
    (array of ones, if not available).

    See Also
    --------
    lb_pidsim_train.utils.nan_filter : 
      Clean arrays from NaN elements.
    """
    ## Input array
    if self.X_vars is not None:
      X = nan_filter ( self._datachunk[self.X_vars] . to_numpy() )
    else:
      X = nan_filter ( self._datachunk . to_numpy() )

    ## Output array
    if self.Y_vars is not None:
      Y = nan_filter ( self._datachunk[self.Y_vars] . to_numpy() )
    else:
      raise ValueError ("No variables have been passed to create an output-set.")

    ## Weight array
    if self.w_var is not None:
      w = self._datachunk[self.w_var] . to_numpy()
    else:
      w = np.ones ( X.shape[0], dtype = NP_FLOAT )

    X . astype ( NP_FLOAT )
    Y . astype ( NP_FLOAT )
    w . astype ( NP_FLOAT )
    return X, Y, w

  @property
  def X_vars (self) -> list:
    """Names of the input variables (`None`, if not available)."""
    return self._X_vars

  @property
  def Y_vars (self) -> list:
    """Names of the output variables (`None`, if not available)."""
    return self._Y_vars

  @property
  def w_var (self) -> list:
    """Name of the weight variable (`None`, if not available)."""
    return self._w_var

  @property
  def datachunk (self) -> pd.DataFrame:
    """Dataset used for the training procedure."""
    return self._datachunk

  @property
  def X (self) -> np.ndarray:
    """Array containing a shuffled version of the input-set."""
    return self._X

  @property
  def Y (self) -> np.ndarray:
    """Array containing a shuffled version of the output-set."""
    return self._Y

  @property
  def w (self) -> np.ndarray:
    """Array containing a shuffled version of the weights 
    (array of ones, if not available)."""
    return self._w



if __name__ == "__main__":   # TODO complete __main__
  handler = DataHandler()
  handler . feed_from_root_files ( "../data/Zmumu.root", ["px1", "py1", "pz1"], "E1" )
  print ( handler.X_vars )
  print ( handler.Y_vars )
  print ( handler.w_var )
  print ( handler.datachunk.describe() )
  print ( handler.prepare_dataset() )
  print ( handler.X )
  print ( handler.Y )
  print ( handler.w )
