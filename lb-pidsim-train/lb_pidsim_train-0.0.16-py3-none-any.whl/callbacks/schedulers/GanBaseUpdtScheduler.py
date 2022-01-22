#from __future__ import annotations

import tensorflow as tf
from tensorflow.keras.callbacks import Callback

K = tf.keras.backend

class GanBaseUpdtScheduler (Callback):   # TODO add docstring
  """class description"""
  def __init__ (self):   # TODO add data-type check
    super().__init__()

  def on_epoch_begin (self, epoch, logs = None):
    ## Discriminator updt-per-batch scheduling
    d_updt_per_batch = K.get_value ( self.model.d_updt_per_batch )
    K.set_value ( self.model._d_updt_per_batch, self._scheduled_updt (d_updt_per_batch, epoch) )

    ## Generator updt-per-batch scheduling
    g_updt_per_batch = K.get_value ( self.model.g_updt_per_batch )
    K.set_value ( self.model._g_updt_per_batch, self._scheduled_updt (g_updt_per_batch, epoch) )

  def _scheduled_updt (self, updt, epoch):
    return updt

  def on_epoch_end (self, epoch, logs = None):
    logs = logs or {}
    logs["d_updt_per_batch"] = K.get_value ( self.model._d_updt_per_batch )
    logs["g_updt_per_batch"] = K.get_value ( self.model._g_updt_per_batch )
