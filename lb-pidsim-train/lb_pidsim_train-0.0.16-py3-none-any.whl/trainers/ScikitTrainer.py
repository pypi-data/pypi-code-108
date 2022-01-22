#from __future__ import annotations

import os
import pickle
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime
from html_reports import Report
from matplotlib.patches import Patch
from lb_pidsim_train.trainers import BaseTrainer
from lb_pidsim_train.metrics import KL_div_from_counts, JS_div_from_counts, KS_test_from_counts, chi2_test_from_counts


NP_FLOAT = np.float32
"""Default data-type for arrays."""


class ScikitTrainer (BaseTrainer):
  def __init__ ( self ,
                 name ,
                 export_dir  = None ,
                 export_name = None ,
                 report_dir  = None ,
                 report_name = None ,
                 verbose = False ) -> None:   # TODO new variable name for warnings
    super().__init__ ( name = name ,
                       export_dir  = export_dir  ,
                       export_name = export_name ,
                       report_dir  = report_dir  ,
                       report_name = report_name ,
                       verbose = verbose )

  def train_model ( self , 
                    model ,
                    validation_split = 0.2 ,
                    performance_metric = "chi2_test" ,
                    plots_on_report = True ,
                    save_model = True ,
                    verbose = 0 ) -> None:   # TODO add docstring
    """"""
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
    self._performance_metric = performance_metric

    ## Sizes computation
    sample_size = self._X . shape[0]
    trainset_size = int ( (1.0 - validation_split) * sample_size )

    ## Training dataset
    train_feats  = self._X_scaled[:trainset_size]
    train_labels = self._Y[:trainset_size] . flatten()
    train_w      = self._w[:trainset_size] . flatten()

    ## Validation dataset
    if validation_split != 0.0:
      val_feats  = self._X_scaled[trainset_size:]
      val_labels = self._Y[trainset_size:] . flatten()
      val_w      = self._w[trainset_size:] . flatten()

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

    self._model = model
    self._scores = [None, None]

    if plots_on_report:
      if validation_split != 0.0:
        report.add_markdown ("## Model performance on validation set")
        self._eff_hist2d (report, bins = 100, validation = True)
        self._eff_hist1d (report, bins = 50, validation = True)
        report.add_markdown ("***")
      report.add_markdown ("## Model performance on training set")
      self._eff_hist2d (report, bins = 100, validation = False)
      self._eff_hist1d (report, bins = 50, validation = False)

    if save_model:
      self._save_model ( "saved_model", model, verbose = (verbose > 0) )

    filename = f"{self._report_dir}/{self._report_name}"
    report . write_report ( filename = f"{filename}.html" )
    if (verbose > 1):
      print (f"Training report correctly exported to {filename}")

  def _eff_hist2d ( self, report, bins = 100, validation = False ) -> None:   # TODO add docstring
    """"""
    X, Y, w, probas = self._data_to_plot ( validation = validation )

    binning = [ np.linspace ( 0 , 100 , bins+1 ) ,   # momentum binning
                np.linspace ( 1 , 6   , bins+1 ) ]   # pseudorapidity binning

    ## Efficiency correction
    plt.figure (figsize = (8,5), dpi = 100)
    plt.title  ("isMuon (Brunel reconstruction)", fontsize = 14)
    plt.xlabel ("Momentum [GeV/$c$]", fontsize = 12)
    plt.ylabel ("Pseudorapidity", fontsize = 12)
    hist2d = np.histogram2d ( X[:,0][Y == 1]/1e3, X[:,1][Y == 1], weights = w[Y == 1], bins = binning )
    plt.pcolormesh ( binning[0], binning[1], hist2d[0].T, cmap = plt.get_cmap ("inferno"), vmin = 0 )

    report.add_figure(); plt.clf(); plt.close()

    ## Efficiency parameterization
    plt.figure (figsize = (8,5), dpi = 100)
    algo_name = self._name . split("_") [0]
    plt.title  (f"isMuon ({algo_name} model)", fontsize = 14)
    plt.xlabel ("Momentum [GeV/$c$]", fontsize = 12)
    plt.ylabel ("Pseudorapidity", fontsize = 12)
    hist2d = np.histogram2d ( X[:,0]/1e3, X[:,1], weights = w * probas, bins = binning )
    plt.pcolormesh ( binning[0], binning[1], hist2d[0].T, cmap = plt.get_cmap ("inferno"), vmin = 0 )

    report.add_figure(); plt.clf(); plt.close()
    # report.add_markdown ("<br/>")

  def _eff_hist1d ( self , 
                    report , 
                    bins = 100 , 
                    validation = False ) -> None:   # TODO add docstring
    """"""
    X, Y, w, probas = self._data_to_plot ( validation = validation )
    p_limits = [0, 4, 8, 12, 100]   ## Momentum limits
    eta_bins = np.linspace (1, 6, bins+1) 

    if not validation:
      self._scores[0] = list()
    else:
      self._scores[1] = list()

    model_name = self._name . split("_") [1]

    for i in range (len(p_limits) - 1):
      fig, ax = plt.subplots (figsize = (8,5), dpi = 100)
      ax.set_title  (f"{model_name} for $p$ in ({p_limits[i]}, {p_limits[i+1]}) GeV/$c$")
      ax.set_xlabel ("Pseudorapidity", fontsize = 12)
      ax.set_ylabel ("Entries", fontsize = 12)
      ax.set_yscale ("log")
  
      custom_handles = list()
      custom_labels = list()
  
      query = (X[:,0]/1e3 > p_limits[i]) & (X[:,0]/1e3 <= p_limits[i+1])   # NumPy query

      ## TurboCalib
      h_all, bin_edges = np.histogram ( X[:,1][query], bins = eta_bins, weights = w[query] )
      bin_centers = ( bin_edges[1:] + bin_edges[:-1] ) / 2
      h_all = np.where ( h_all > 0, h_all, 0 )   # ensure positive entries
      h_all = h_all . astype (np.int32)           # ensure integer entries
      ax.errorbar ( bin_centers, h_all, yerr = 0.0, color = "red", drawstyle = "steps-mid", zorder = 2 )
      custom_handles . append ( Patch (facecolor = "white", alpha = 0.8, edgecolor = "red") )
      custom_labels  . append ( "TurboCalib" )
  
      ## Efficiency parameterization
      h_pred, bin_edges = np.histogram ( X[:,1][query], bins = eta_bins, weights = w[query] * probas[query] )
      bin_centers = ( bin_edges[1:] + bin_edges[:-1] ) / 2
      h_pred = np.where ( h_pred > 0, h_pred, 0 )   # ensure positive entries
      h_pred = h_pred . astype (np.int32)           # ensure integer entries
      ax.errorbar ( bin_centers, h_pred, yerr = 0.0, color = "royalblue", drawstyle = "steps-mid", zorder = 1 )
      custom_handles . append ( Patch (facecolor = "white", alpha = 0.8, edgecolor = "royalblue") )
      custom_labels  . append ( f"{model_name} model" )
  
      ## Efficiency correction
      h_true, bin_edges = np.histogram ( X[:,1][query][Y[query] == 1], bins = eta_bins,
                                         weights = w[query][Y[query] == 1] )
      bin_centers = ( bin_edges[1:] + bin_edges[:-1] ) / 2
      h_true = np.where ( h_true > 0, h_true, 0 )   # ensure positive entries
      h_true = h_true . astype (np.int32)           # ensure integer entries
      ax.errorbar ( bin_centers, h_true, yerr = h_true**0.5, fmt = '.', color = "black", 
                    barsabove = True, capsize = 2, label = f"{model_name} passed", zorder = 0 )
      handles, labels = ax.get_legend_handles_labels()
      custom_handles . append ( handles[-1] )
      custom_labels  . append ( labels[-1] )
  
      ax.legend (handles = custom_handles, labels = custom_labels, loc = "upper right", fontsize = 10)
      report.add_figure(); plt.clf(); plt.close()
      # report.add_markdown ("<br/>")

      score = self._compute_score ( h_pred, h_true, strategy = self._performance_metric )

      if not validation:
        self._scores[0] . append ( score )
      else:
        self._scores[1] . append ( score )

  def _data_to_plot (self, validation = False) -> tuple:   # TODO complete docstring
    """...
    
    Parameters
    ----------  
    validation : `bool`
      ...
      
    Returns
    -------
    X : `np.ndarray`
      ...

    Y : `np.ndarray`
      ...

    w : `np.ndarray`
      ...

    probas : `np.ndarray`
      ...
    """
    sample_size = self._X . shape[0]
    trainset_size = int ( (1.0 - self._validation_split) * sample_size )
    if not validation:
      X, X_scaled = self._X[:trainset_size], self._X_scaled[:trainset_size]
      Y, w = self._Y[:trainset_size], self._w[:trainset_size]
    else:
      if self._validation_split == 0.0:
        raise ValueError ("error.")   # TODO add error message
      X, X_scaled = self._X[trainset_size:], self._X_scaled[trainset_size:]
      Y, w = self._Y[trainset_size:], self._w[trainset_size:]
    probas = self.model.predict_proba ( X_scaled ) [:,1]
    return X, Y.flatten(), w.flatten(), probas.flatten()

  def _compute_score ( self ,
                       h_pred ,
                       h_true ,
                       strategy = "ks_test" ) -> float:   # TODO add docstring
    """short description"""
    if strategy == "chi2_test":
      score = chi2_test_from_counts (h_pred, h_true)
    elif strategy == "ks_test":
      score = KS_test_from_counts (h_pred, h_true)
    elif strategy == "kl_div":
      score = KL_div_from_counts (h_pred, h_true)
    elif strategy == "js_div":
      score = JS_div_from_counts (h_pred, h_true)
    else:
      ValueError ("error.")   # TODO add error message
    return score

  def _save_model ( self, name, model, verbose = False ) -> None:   # TODO complete docstring
    """Save the trained model.
    
    Parameters
    ----------
    name : `str`
      Name of the pickle file containing the Scikit-Learn model.

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
    if verbose: print ( f"Trained model correctly exported to {filename}" )

  @property
  def model (self):
    """The model after the training procedure."""
    return self._model

  @property
  def scores (self) -> list:
    """Model quality scores on training and validation sets."""
    return self._scores
