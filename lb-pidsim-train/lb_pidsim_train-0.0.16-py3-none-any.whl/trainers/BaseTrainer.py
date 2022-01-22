#from __future__ import annotations

import os
import pickle
import numpy as np

from time import time
from warnings import warn
from datetime import datetime
from lb_pidsim_train.trainers import DataHandler
from lb_pidsim_train.utils    import preprocessor
from lb_pidsim_train.utils    import warn_message as wm


class BaseTrainer (DataHandler):   # TODO class description
  """Base class for training models.
  
  Parameters
  ----------
  name : `str`
    Name of the trained model.

  export_dir : `str`, optional
    Export directory for the trained model.

  export_name : `str`, optional
    Export file name for the trained model.

  report_dir : `str`, optional
    Report directory for the trained model.

  report_name : `str`, optional
    Report file name for the trained model.

  verbose : `bool`, optional
    Verbosity mode. `False` = silent (default), 
    `True` = warning messages are enabled. 
  """
  def __init__ ( self ,
                 name ,
                 export_dir  = None ,
                 export_name = None ,
                 report_dir  = None ,
                 report_name = None ,
                 verbose = False ) -> None:   # TODO new variable name for warnings
    ## Switch off all flags
    super().__init__()
    self._model_trained = False

    timestamp = str (datetime.now()) . split (".") [0]
    timestamp = timestamp . replace (" ","_")
    version = ""
    for time, unit in zip ( timestamp.split(":"), ["h","m","s"] ):
      version += time + unit   # YYYY-MM-DD_HHhMMmSSs

    self._name = f"{name}"

    if export_dir is None:
      export_dir = "./models"
      message = wm.name_not_passed ("export dirname", export_dir)
      if verbose: warn (message)
    self._export_dir = export_dir
    if not os.path.exists (self._export_dir):
      message = wm.directory_not_found (self._export_dir)
      if verbose: warn (message)
      os.makedirs (self._export_dir)

    if export_name is None:
      export_name = f"{name}_{version}"
      message = wm.name_not_passed ("export filename", export_name)
      if verbose: warn (message)
    self._export_name = export_name

    if report_dir is None:
      report_dir = "./reports"
      message = wm.name_not_passed ("report dirname", report_dir)
      if verbose: warn (message)
    self._report_dir = report_dir
    if not os.path.exists (self._report_dir):
      message = wm.directory_not_found (self._report_dir)
      if verbose: warn (message)
      os.makedirs (self._report_dir)

    if report_name is None:
      report_name = f"{name}_{version}"
      message = wm.name_not_passed ("report filename", report_name)
      if verbose: warn (message)
    self._report_name = report_name

  def prepare_dataset ( self ,
                        X_preprocessing = None ,
                        Y_preprocessing = None ,
                        X_vars_to_preprocess = None ,
                        Y_vars_to_preprocess = None ,
                        subsample_size = 100000 ,
                        save_transformer = True ,
                        verbose = 0 ) -> None:
    """Split the data-chunk into X, Y and w, and perform preprocessing.

    Parameters
    ----------
    X_preprocessing : {None, 'minmax', 'standard', 'quantile'}, optional
      Preprocessing strategy for the input-set. The choices are `None` 
      (default), `'minmax'`, `'standard'` and `'quantile'`. If `None` is
      selected, no preprocessing is performed at all.

    Y_preprocessing : {None, 'minmax', 'standard', 'quantile'}, optional
      Preprocessing strategy for the output-set. The choices are `None` 
      (default), `'minmax'`, `'standard'` and `'quantile'`. If `None` is
      selected, no preprocessing is performed at all.

    X_vars_to_preprocess : `str` or `list` of `str`, optional
      List of input variables to preprocess (`None`, by default). If `None` 
      is selected, all the input variables are preprocessed.

    Y_vars_to_preprocess : `str` or `list` of `str`, optional
      List of output variables to preprocess (`None`, by default). If `None` 
      is selected, all the output variables are preprocessed.

    subsample_size : `int`, optional
      Data-chunk subsample size used to compute the preprocessing transformer 
      parameters (`100000`, by default).

    save_transformer : `bool`, optional
      Boolean flag to save and export the transformers, if preprocessing 
      is enabled (`True`, by default).

    verbose : {0, 1, 2}, optional
      Verbosity mode. `0` = silent (default), `1` = control messages after 
      transformers saving is printed, `2`= also times for shuffling and 
      preprocessing are printed. 

    See Also
    --------
    lb_pidsim_train.utils.preprocessor :
      Scikit-Learn transformer for data preprocessing.
    """
    super().prepare_dataset (verbose = verbose)
    self._dataset_prepared = False   # switch off dataset prepared flag

    ## Data-type control
    try:
      subsample_size = int ( subsample_size )
    except:
      raise TypeError ("The sub-sample size should be an integer.")

    ## Preprocessed input array
    if X_preprocessing is not None:
      start = time()
      if X_vars_to_preprocess is not None:
        X_cols_to_preprocess = list()
        for idx, var in enumerate (self._X_vars):
          if var in X_vars_to_preprocess:
            X_cols_to_preprocess . append (idx)   # column index
      else:
        X_cols_to_preprocess = None
      self._scaler_X = preprocessor ( self.X[:subsample_size], strategy = X_preprocessing, 
                                      cols_to_transform = X_cols_to_preprocess )
      self._X_scaled = self._scaler_X . transform (self.X)   # transform the input-set
      stop = time()
      if (verbose > 1): 
        print ( f"Preprocessing time for X: {stop-start:.3f} s" )
      if save_transformer: 
        self._save_transformer ( "transform_X" , 
                                 self._scaler_X.sklearn_transformer ,   # saved as Scikit-Learn class
                                 verbose = (verbose > 0) )
    else:
      self._scaler_X = None
      self._X_scaled = self.X

    ## Preprocessed output array
    if Y_preprocessing is not None:
      start = time()
      if Y_vars_to_preprocess is not None:
        Y_cols_to_preprocess = list()
        for idx, var in enumerate (self._Y_vars):
          if var in Y_vars_to_preprocess:
            Y_cols_to_preprocess . append (idx)   # column index
      else:
        Y_cols_to_preprocess = None
      self._scaler_Y = preprocessor ( self.Y[:subsample_size], strategy = Y_preprocessing, 
                                      cols_to_transform = Y_cols_to_preprocess )
      self._Y_scaled = self._scaler_Y . transform (self.Y)   # transform the output-set
      stop = time()
      if (verbose > 1): 
        print ( f"Preprocessing time for Y: {stop-start:.3f} s" )
      if save_transformer:
        self._save_transformer ( "transform_Y" , 
                                 self._scaler_Y.sklearn_transformer ,   # saved as Scikit-Learn class 
                                 verbose = (verbose > 0) )
    else:
      self._scaler_Y = None
      self._Y_scaled = self.Y

    self._dataset_prepared = True # switch on dataset prepared flag

  def _save_transformer (self, name, transformer, verbose = False) -> None:
    """Save the preprocessing transformer.
    
    Parameters
    ----------
    name : `str`
      Name of the pickle file containing the Scikit-Learn transformer.

    transformer : `lb_pidsim_train.utils.CustomColumnTransformer`
      Preprocessing transformer resulting from `lb_pidsim_train.utils.preprocessor`.

    verbose : `bool`, optional
      Verbosity mode. `False` = silent (default), `True` = a control message is printed. 

    See Also
    --------
    lb_pidsim_train.utils.preprocessor :
      Scikit-Learn transformer for data preprocessing.
    """
    dirname = f"{self._export_dir}/{self._export_name}"
    if not os.path.exists (dirname):
      os.makedirs (dirname)
    filename = f"{dirname}/{name}.pkl"
    pickle . dump ( transformer, open (filename, "wb") )
    if verbose: print ( f"Transformer correctly exported to {filename}" )

  def train_model (self) -> None:   # TODO add docstring
    """short description"""
    raise NotImplementedError ("error")   # TODO add error message

  @property
  def X_scaled (self) -> np.ndarray:
    """Array containing a preprocessed version of the input-set."""
    return self._X_scaled

  @property
  def Y_scaled (self) -> np.ndarray:
    """Array containing a preprocessed version of the output-set."""
    return self._Y_scaled

    

if __name__ == "__main__":   # TODO complete __main__
  trainer = BaseTrainer ( "test", export_dir = "./models", report_dir = "./reports" )
  trainer . feed_from_root_files ( "../data/Zmumu.root", ["px1", "py1", "pz1"], "E1" )
  print ( trainer.datachunk.describe() )
