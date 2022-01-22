#from __future__ import annotations

import os
import pickle
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt

from time import time
from sklearn.utils import shuffle
from lb_pidsim_train.trainers import TensorTrainer
from lb_pidsim_train.utils import PidsimColTransformer


NP_FLOAT = np.float32
"""Default data-type for arrays."""

TF_FLOAT = tf.float32
"""Default data-type for tensors."""


class GanTrainer (TensorTrainer):   # TODO class description
  def load_model ( self , 
                   filepath , 
                   model_name = "saved_model" ,
                   verbose = 0 ) -> None:   # TODO add docstring
    """"""
    if not self._datachunk_filled:
      raise RuntimeError ("error")   # TODO implement error message
    
    if self._dataset_prepared:
      raise RuntimeError ("error")   # TODO implement error message

    ## Unpack data
    X, Y, w = self._unpack_data()
    start = time()
    X, Y, w = shuffle (X, Y, w)
    stop = time()
    if verbose: print ( f"Shuffle-time: {stop-start:.3f} s" )

    self._X = X
    self._Y = Y
    self._w = w

    ## Preprocessed input array
    file_X = f"{filepath}/transform_X.pkl"
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
      self._X_scaled = self.X

    ## Preprocessed output array
    file_Y = f"{filepath}/transform_Y.pkl"
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
      self._Y_scaled = self.Y

    ## Load the generator
    self._generator = tf.keras.models.load_model (f"{filepath}/{model_name}")
    self._model_loaded = True
  
  def extract_generator ( self, fine_tuned_layers = None ) -> list:   # TODO add docstring
    """"""
    if not self._model_loaded:
      raise RuntimeError ("error")   # TODO implement error message

    num_g_layers = len ( self._generator.layers[:-1] )

    ## Data-type control
    if fine_tuned_layers is not None:
      try:
        fine_tuned_layers = int ( fine_tuned_layers )
      except:
        raise TypeError (f"The number of layers to fine-tune should be an integer," 
                         f" instead {type(fine_tuned_layers)} passed." )
    else:
      fine_tuned_layers = num_g_layers

    g_layers = list()
    for i, layer in enumerate ( self._generator.layers[:-1] ):
      layer._name = f"loaded_{layer.name}"
      if i < (num_g_layers - fine_tuned_layers): 
        layer.trainable = False
      else:
        layer.trainable = True
      g_layers . append (layer)

    return g_layers

  def train_model ( self , 
                    model , 
                    batch_size = 1 , 
                    num_epochs = 1 , 
                    validation_split = 0.0 , 
                    scheduler = None , 
                    plots_on_report = True , 
                    save_model = True , 
                    verbose = 0 ) -> None:
    super().train_model ( model = model , 
                          batch_size = 2 * batch_size , 
                          num_epochs = num_epochs , 
                          validation_split = validation_split , 
                          scheduler = scheduler , 
                          plots_on_report = plots_on_report , 
                          save_model = save_model , 
                          verbose = verbose )

  def _training_plots (self, report, history) -> None:   # TODO complete docstring
    """short description
    
    Parameters
    ----------
    report : ...
      ...

    history : ...
      ...

    See Also
    --------
    html_reports.Report : ...
      ...
    """
    n_epochs = len (history.history["mse"])

    ## Metric curves plots
    plt.figure (figsize = (8,5), dpi = 100)
    plt.title  ("Metric curves", fontsize = 14)
    plt.xlabel ("Training epochs", fontsize = 12)
    plt.ylabel ("Mean square error", fontsize = 12)
    plt.plot (history.history["mse"], linewidth = 1.5, color = "forestgreen", label = "training set")
    if self._validation_split != 0.0:
      plt.plot (history.history["val_mse"], linewidth = 1.5, color = "orangered", label = "validation set")
    plt.legend (loc = "upper right", fontsize = 10)
    y_bottom = min ( min(history.history["mse"][int(n_epochs/10):]), min(history.history["val_mse"][int(n_epochs/10):]) )
    y_top    = max ( max(history.history["mse"][int(n_epochs/10):]), max(history.history["val_mse"][int(n_epochs/10):]) )
    y_bottom -= 0.1 * y_bottom
    y_top    += 0.1 * y_top
    plt.ylim (bottom = y_bottom, top = y_top)

    report.add_figure(); plt.clf(); plt.close()
    # report.add_markdown ("<br/>")

    ## Learning curves plots
    plt.figure (figsize = (8,5), dpi = 100)
    plt.title  ("Learning curves", fontsize = 14)   # TODO plot loss variance
    plt.xlabel ("Training epochs", fontsize = 12)
    plt.ylabel (f"{self.model.loss_name}", fontsize = 12)
    plt.plot (history.history["d_loss"], linewidth = 1.5, color = "dodgerblue", label = "discriminator")
    plt.plot (history.history["g_loss"], linewidth = 1.5, color = "coral", label = "generator")
    plt.legend (title = "Training players:", loc = "upper right", fontsize = 10)
    y_bottom = min ( min(history.history["d_loss"][int(n_epochs/10):]), min(history.history["g_loss"][int(n_epochs/10):]) )
    y_top    = max ( max(history.history["d_loss"][int(n_epochs/10):]), max(history.history["g_loss"][int(n_epochs/10):]) )
    y_bottom += 0.1 * y_bottom
    y_top    += 0.1 * y_top
    plt.ylim (bottom = y_bottom, top = y_top)

    report.add_figure(); plt.clf(); plt.close()
    # report.add_markdown ("<br/>")

    ## Learning rate scheduling plots
    plt.figure (figsize = (8,5), dpi = 100)
    plt.title  ("Learning rate scheduling", fontsize = 14)
    plt.xlabel ("Training epochs", fontsize = 12)
    plt.ylabel ("Learning rate", fontsize = 12)
    plt.plot (history.history["d_lr"], linewidth = 1.5, color = "dodgerblue", label = "discriminator")
    plt.plot (history.history["g_lr"], linewidth = 1.5, color = "coral", label = "generator")
    plt.legend (title = "Training players:", loc = "upper right", fontsize = 10)

    report.add_figure(); plt.clf(); plt.close()
    # report.add_markdown ("<br/>")

    ## Validation plots
    rows = cols = len(self.Y_vars)
    fig, ax = plt.subplots (rows, cols, figsize = (14,12), dpi = 200)
    plt.subplots_adjust (wspace = 0.35, hspace = 0.25)

    titles = self.Y_vars
    Y_ref  = self.Y
    Y_gen  = self._scaler_Y . inverse_transform ( self.generate (self.X_scaled) )
    
    for i in range(rows):
      for j in range(cols):
        ax[i,j] . tick_params (labelsize = 6)
        if i == j:
          ax[i,j] . set_xlabel (titles[i], fontsize = 8)
          _, b, _ = ax[i,j] . hist (Y_ref[:,i], bins = 100, density = True, weights = self.w, color = "dodgerblue", label = "Original")
          ax[i,j] . hist (Y_gen[:,i], bins = b, density = True, histtype = "step", color = "deeppink", label = "Generated")
          ax[i,j] . legend (loc = "upper left", fontsize = 6)
        elif i > j:
          ax[i,j] . set_xlabel (titles[j], fontsize = 8)
          ax[i,j] . set_ylabel (titles[i], fontsize = 8)
          ax[i,j] . scatter (Y_ref[:,j], Y_ref[:,i], s = 1, alpha = 0.01, color = "dodgerblue")   # TODO fix sWeight bug
          ax[i,j] . scatter (Y_gen[:,j], Y_gen[:,i], s = 1, alpha = 0.01, color = "deeppink")
        elif i < j:
          ax[i,j] . set_xlabel (titles[j], fontsize = 8)
          ax[i,j] . set_ylabel (titles[i], fontsize = 8)
          ax[i,j] . scatter (Y_gen[:,j], Y_gen[:,i], s = 1, alpha = 0.01, color = "deeppink")
          ax[i,j] . scatter (Y_ref[:,j], Y_ref[:,i], s = 1, alpha = 0.01, color = "dodgerblue")

    report.add_figure(); plt.clf(); plt.close()
    # report.add_markdown ("<br/>")

  def _save_model ( self, name, model, verbose = False ) -> None:   # TODO fix docstring
    """Save the trained generator.
    
    Parameters
    ----------
    name : `str`
      Name of the directory containing the TensorFlow SavedModel file.

    model : `tf.keras.Model`
      GAN model taken from `lb_pidsim_train.algorithms.gan` and configured 
      for the training procedure.

    verbose : `bool`, optional
      Verbosity mode. `False` = silent (default), `True` = a control message 
      is printed. 

    See Also
    --------
    lb_pidsim_train.algorithms.gan :
      ...

    tf.keras.Model :
      Set of layers with training and inference features.

    tf.keras.models.save_model :
      Save a model as a TensorFlow SavedModel or HDF5 file.
    """
    dirname = f"{self._export_dir}/{self._export_name}"
    if not os.path.exists (dirname):
      os.makedirs (dirname)
    filename = f"{dirname}/{name}"
    model.generator . save ( f"{filename}", save_format = "tf" )
    if verbose: print ( f"Trained generator correctly exported to {filename}" )

  def generate (self, X) -> np.ndarray:   # TODO complete docstring
    """Method to generate the target variables `Y` given the input features `X`.
    
    Parameters
    ----------
    X : `np.ndarray` or `tf.Tensor`
      ...

    Returns
    -------
    Y : `np.ndarray`
      ...
    """
    ## Data-type control
    if isinstance (X, np.ndarray):
      X = tf.convert_to_tensor ( X, dtype = TF_FLOAT )
    elif isinstance (X, tf.Tensor):
      X = tf.cast (X, dtype = TF_FLOAT)
    else:
      TypeError ("error")  # TODO insert error message

    ## Sample random points in the latent space
    batch_size = tf.shape(X)[0]
    latent_dim = self.model.latent_dim
    latent_tensor = tf.random.normal ( shape = (batch_size, latent_dim), dtype = TF_FLOAT )

    ## Map the latent space into the generated space
    input_tensor = tf.concat ( [X, latent_tensor], axis = 1 )
    Y = self.model.generator (input_tensor) 
    Y = Y.numpy() . astype (NP_FLOAT)   # casting to numpy array
    return Y

  @property
  def discriminator (self) -> tf.keras.Sequential:
    """The discriminator after the training procedure."""
    return self.model.discriminator

  @property
  def generator (self) -> tf.keras.Sequential:
    """The generator after the training procedure."""
    return self.model.generator



if __name__ == "__main__":   # TODO complete __main__
  trainer = GanTrainer ( "test", export_dir = "./models", report_dir = "./reports" )
  trainer . feed_from_root_files ( "../data/Zmumu.root", ["px1", "py1", "pz1"], "E1" )
  print ( trainer.datachunk.describe() )
