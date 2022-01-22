#from __future__ import annotations

import os
import pickle
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from time import time
from warnings import warn
from datetime import datetime
from html_reports import Report
from sklearn.utils import shuffle
from lb_pidsim_train.trainers import BaseTrainer
from lb_pidsim_train.utils import warn_message as wm
from lb_pidsim_train.utils import PidsimColTransformer
from lb_pidsim_train.metrics import KL_div, JS_div, KS_test, chi2_test


NP_FLOAT = np.float32
"""Default data-type for arrays."""

TF_FLOAT = tf.float32
"""Default data-type for tensors."""


class ScikitClassifier (BaseTrainer):   # TODO class description
  def __init__ ( self , 
                 name ,
                 model_dir  ,
                 model_name , 
                 export_dir  = None , 
                 export_name = None , 
                 report_dir  = None , 
                 report_name = None , 
                 verbose = False ) -> None:
    ## Switch off all flags
    self._datachunk_filled = False
    self._dataset_prepared = False
    self._model_trained = False

    self._model_dir  = model_dir    # TODO check existence
    self._model_name = model_name   # TODO add default value
    self._generator  = tf.keras.models.load_model (f"{model_dir}/{model_name}/saved_model")

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
      model_dirname = f"{model_dir}".split("/")[-1]
      export_name = f"{name}_{model_dirname}"
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
      model_dirname = f"{model_dir}".split("/")[-1]
      report_name = f"{name}_{model_dirname}"
      message = wm.name_not_passed ("report filename", report_name)
      if verbose: warn (message)
    self._report_name = report_name

  def prepare_dataset (self, verbose = 0) -> None:   # TODO complete docstring
    """Split the data-chunk into X, Y and w, and perform the saved preprocessing.
    
    Parameters
    ----------
    verbose : {0, 1, 2}, optional
      Verbosity mode. `0` = silent (default), `1` = control messages after 
      transformers loading is printed, `2`= also times for shuffling and 
      preprocessing are printed.
    """
    super().prepare_dataset ( X_preprocessing = None ,
                              Y_preprocessing = None ,
                              verbose = verbose )
    self._dataset_prepared = False   # switch off dataset prepared flag

    ## Preprocessed input array
    file_X = f"{self._model_dir}/{self._model_name}/transform_X.pkl"
    if os.path.exists (file_X):
      start = time()
      self._scaler_X = PidsimColTransformer ( pickle.load (open (file_X, "rb")) )
      if (verbose > 0):
        print (f"Transformer correctly loaded from {file_X}.")
      self._X_scaled = self._scaler_X . transform ( self.X )
      stop = time()
      if (verbose > 1):
        print (f"Preprocessing time for X: {stop-start:.3f} s")
    else:
      self._scaler_X = None

    ## Preprocessed output array
    file_Y = f"{self._model_dir}/{self._model_name}/transform_Y.pkl"
    if os.path.exists (file_Y):
      start = time()
      self._scaler_Y = PidsimColTransformer ( pickle.load (open (file_Y, "rb")) )
      if (verbose > 0):
        print (f"Transformer correctly loaded from {file_Y}.")
      self._Y_scaled = self._scaler_Y . transform ( self.Y )
      stop = time()
      if (verbose > 1):
        print (f"Preprocessing time for Y: {stop-start:.3f} s")
    else:
      self._scaler_Y = None

    self._dataset_prepared = True   # switch on dataset prepared flag

  def train_model ( self ,
                    model ,
                    validation_split = 0.2 ,
                    inverse_transform = False ,
                    performance_metric = "ks_test" ,
                    plots_on_report = True ,
                    save_model = True ,
                    verbose = 0 ) -> None:   # TODO add docstring
    if not self._dataset_prepared:
      raise RuntimeError ("error")   # TODO implement error message

    report = Report()   # TODO add hyperparams to the report

    ## Data-type control
    try:
      validation_split = float ( validation_split )
    except:
      raise TypeError ( f"The fraction of train-set used for validation should"
                        f" be a float, instead {type(validation_split)} passed." )

    ## Data-value control
    if (validation_split < 0.0) or (validation_split > 1.0):
      raise ValueError ("error")   # TODO add error message

    if performance_metric not in ["kl_div", "js_div", "ks_test", "chi2_test"]:
      raise ValueError ("error")   # TODO add error message

    self._validation_split = validation_split

    ## Sizes computation
    sample_size = self._X . shape[0]
    trainset_size = int ( (1.0 - validation_split) * sample_size )

    ## Training dataset
    trainset = ( self._X_scaled[:trainset_size], self._Y_scaled[:trainset_size], self._w[:trainset_size] )
    train_feats, train_labels, train_w = self._rearrange_dataset ( data = trainset , 
                                                                   inverse_transform = inverse_transform )

    ## Validation dataset
    if validation_split != 0.0:
      valset = ( self._X_scaled[trainset_size:], self._Y_scaled[trainset_size:], self._w[trainset_size:] )
      val_feats, val_labels, val_w = self._rearrange_dataset ( data = valset , 
                                                               inverse_transform = inverse_transform )

    ## Training procedure
    start = datetime.now()
    model . fit (train_feats, train_labels, sample_weight = train_w)
    self._model_trained = True   # switch on model trained flag
    stop  = datetime.now()
    if (verbose > 0): 
      timestamp = str(stop-start) . split (".") [0]   # HH:MM:SS
      timestamp = timestamp . split (":")   # [HH, MM, SS]
      timestamp = f"{timestamp[0]}h {timestamp[1]}min {timestamp[2]}s"
      print (f"Classifier training completed in {timestamp}.")

    self._model  = model
    self._scores = [None, None]

    result = { "weights"     : train_w ,
               "true_labels" : train_labels ,
               "pred_labels" : model.predict (train_feats) ,
               "pred_probas" : model.predict_proba (train_feats) }

    if validation_split != 0.0:
      result.update ( { "val_weights"     : val_w ,
                        "val_true_labels" : val_labels ,
                        "val_pred_labels" : model.predict (val_feats) ,
                        "val_pred_probas" : model.predict_proba (val_feats) } )

    self.scores[0] = self._compute_score ( result = result , 
                                           validation = False , 
                                           strategy = performance_metric ,
                                           bins = 100 )
    if self._validation_split != 0.0:
      self.scores[1] = self._compute_score ( result = result , 
                                             validation = True , 
                                             strategy = performance_metric ,
                                             bins = 100 )

    if plots_on_report:
      self._proba_plots (result, report, bins = 100, strategy = performance_metric)

    if save_model:
      self._save_model ( "saved_model", model, verbose = (verbose > 0) )

    filename = f"{self._report_dir}/{self._report_name}"
    report . write_report ( filename = f"{filename}.html" )
    if (verbose > 1):
      print (f"Training report correctly exported to {filename}")

  def _rearrange_dataset ( self , 
                           data , 
                           inverse_transform = False ) -> tuple:   # TODO add docstring
    """short description"""
    ## Size from latent space
    batch_size = int ( data[0].shape[0] / 2 )
    latent_dim = int ( self._generator.input_shape[1] - self.X.shape[1] )

    ## Latent space --> generated space
    X_gen = tf.convert_to_tensor ( data[0][:batch_size], dtype = TF_FLOAT )
    latent_tensor = tf.random.normal ( shape = (batch_size, latent_dim), dtype = TF_FLOAT )
    input_tensor  = tf.concat ( [X_gen, latent_tensor], axis = 1 )
    output_tensor = self._generator ( input_tensor )

    ## Output arrays
    Y_gen = output_tensor . numpy()
    Y_ref = data[1][batch_size:] . astype (NP_FLOAT)

    ## Feature space
    X = data[0] . astype (NP_FLOAT)
    Y = np.concatenate ( [Y_gen, Y_ref], axis = 0 ) . astype (NP_FLOAT)
    if inverse_transform:
      X = self._scaler_X . inverse_transform (X)
      Y = self._scaler_Y . inverse_transform (Y)

    ## Classification datasets
    feats = np.c_ [ X , Y ]
    labels = np.concatenate ( [ np.ones (Y_gen.shape[0]) , np.zeros (Y_ref.shape[0]) ] )
    weights = data[2] . astype (NP_FLOAT) . reshape (labels.shape)
    
    feats, labels, weights = shuffle (feats, labels, weights)
    return feats, labels, weights

  def _compute_score ( self , 
                       result ,
                       validation = False   ,
                       strategy = "ks_test" , 
                       bins = 100 ) -> float:   # TODO add docstring
    """short description"""
    p_gen, p_ref, w_gen, w_ref = self._class_probas (result, validation = validation)

    if strategy == "ks_test":
      score = KS_test (p_gen, p_ref, bins, w_gen, w_ref) . max()
    elif strategy == "kl_div":
      score = KL_div (p_gen, p_ref, bins, w_gen, w_ref) . max()
    elif strategy == "js_div":
      score = JS_div (p_gen, p_ref, bins, w_gen, w_ref) . max()
    elif strategy == "chi2_test":
      score = chi2_test (p_gen, p_ref, bins, w_gen, w_ref) . max()
    else:
      ValueError ("error.")   # TODO add error message
    return score

  def _class_probas (self, result, validation = False) -> tuple:   # TODO add docstring
    """short description"""
    if not validation:
      p_gen = result["pred_probas"][:,1][result["true_labels"] == 1]
      p_ref = result["pred_probas"][:,1][result["true_labels"] == 0]
      w_gen = result["weights"][result["true_labels"] == 1]
      w_ref = result["weights"][result["true_labels"] == 0]
    else:
      if self._validation_split == 0.0:
        raise ValueError ("error.")   # TODO add error message
      p_gen = result["val_pred_probas"][:,1][result["val_true_labels"] == 1]
      p_ref = result["val_pred_probas"][:,1][result["val_true_labels"] == 0]
      w_gen = result["val_weights"][result["val_true_labels"] == 1]
      w_ref = result["val_weights"][result["val_true_labels"] == 0]
    return p_gen, p_ref, w_gen, w_ref

  def _proba_plots ( self , 
                     result , 
                     report , 
                     bins = 100 , 
                     strategy = "ks_test" ) -> None:   # TODO add docstring
    """short description"""
    ## Class probabilities
    train_p_gen, train_p_ref, train_w_gen, train_w_ref = self._class_probas (result, validation = False)
    train_w_gen /= len(train_w_gen) ; train_w_ref /= len(train_w_ref)
    if self._validation_split != 0.0:
      val_p_gen, val_p_ref, val_w_gen, val_w_ref = self._class_probas (result, validation = True)
      val_w_gen /= len(val_w_gen) ; val_w_ref /= len(val_w_ref)

    ## Score computation
    score = self._compute_score ( result = result , 
                                  validation = (self._validation_split != 0.0) , 
                                  strategy = strategy ,
                                  bins = bins )

    ## Metric names
    if strategy == "ks_test":
      metric_name = "K-S test"
    elif strategy == "kl_div":
      metric_name = "K-L div"
    elif strategy == "js_div":
      metric_name = "J-S div"
    else:
      ValueError ("error.")   # TODO add error message

    ## Plot histograms
    h_0 = h_1 = h_2 = 0.0
    plt.figure (figsize = (8,5), dpi = 100)
    plt.title  ("Class probability distributions", fontsize = 14)
    plt.xlabel ("Predicted probability for GEN-class", fontsize = 12)
    plt.ylabel ("Normalized entries", fontsize = 12)

    if self._validation_split != 0.0:
      h_0 = plt.hist (val_p_ref, bins = bins, range = (0, 1), weights = val_w_ref,
                      color = "royalblue", alpha = 0.5, label = "Reference validation set")
      h_1 = plt.hist (val_p_gen, bins = bins, range = (0, 1), weights = val_w_gen,
                      color = "deeppink", alpha = 0.5, label = "Generated validation set")
      h_2 = plt.hist (train_p_gen, bins = bins, range = (0, 1), weights = train_w_gen,
                      color = "deeppink", histtype = "step", label = "Generated training set")
    else:
      h_0 = plt.hist (train_p_ref, bins = bins, range = (0, 1), weights = train_w_ref,
                      color = "royalblue", alpha = 0.5, label = "Reference training set")
      h_1 = plt.hist (train_p_gen, bins = bins, range = (0, 1), weights = train_w_gen,
                      color = "deeppink", alpha = 0.5, label = "Generated training set")
    
    plt.legend (loc = "upper left", fontsize = 10)
    h_max = max ( max(h_0[0]), max(h_1[0]), max(h_2[0]) )
    plt.text (0.05, 0.75 * h_max, f"{metric_name}: {score:.3f}", fontsize = 12)   # TODO add box for text
    report.add_figure(); plt.clf(); plt.close()

  def _save_model ( self, name, model, verbose = False ) -> None:   # TODO complete docstring
    """Save the trained classifier.
    
    Parameters
    ----------
    name : `str`
      Name of the pickle file containing the Scikit-Learn classifier.

    model : ...
      ...

    verbose : `bool`, optional
      Verbosity mode. `False` = silent (default), `True` = a control message is printed.
    """
    dirname = f"{self._export_dir}/{self._export_name}"
    if not os.path.exists (dirname):
      os.makedirs (dirname)
    filename = f"{dirname}/{name}.pkl"
    pickle . dump ( model, open (filename, "wb") )
    if verbose: print ( f"Trained classifier correctly exported to {filename}" )

  @property
  def model (self):
    """The classifier after the training procedure."""
    return self._model

  @property
  def scores (self) -> list:
    """Model quality scores on training and validation sets."""
    return self._scores



if __name__ == "__main__":   # TODO complete __main__
  print ("Work in progress")
