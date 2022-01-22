"""
  AddRandomFeatures 
  A layer intended for Keras Sequential model to extend a tensor 
  with random features. This is specially useful for generative models. 
"""
from __future__ import print_function 
from __future__ import absolute_import 

import tensorflow as tf
import numpy as np 

from scipy.special import erfinv as ierf 

class AddRandomFeatures ( tf.keras.layers.Layer ) :
  """
    AddRandomFeatures, a layer intended for Keras Sequetial model
    to extend a tensor with random features. 
  """
  def __init__ ( self, n_uniform=0, n_normal=0, **kwargs ):
    """
      Constructor of the Layer object. 
      Arguments.
        n_uniform - int
          Number of features to add and randomize according 
          to a uniform distribution (between 0 and 1)
        n_normal - int 
          Number of features to add and randomize accoring 
          to a normal distribution (mean = 0, sigma = 1). 
    """
    self.cfg = dict() 
    self.cfg['n_uniform'] = n_uniform
    self.cfg['n_normal']  = n_normal

    tf.keras.layers.Layer.__init__ ( self )

  def build ( self, input_shape ):
    """
      Builds the layer when model building is invoked. 
    """
    return tf.keras.layers.Layer.build ( self, input_shape )

  def call ( self, X ):
    """
      Merges to the input tensor with a random tensor having the
      same shape as the input, with the exception of the last dimension
      which is obtained from n_uniform + n_normal. 
    """
    shape_in = tf.shape(X)
    shape_uniform = tf.concat ( (shape_in[:-1], [self.cfg['n_uniform']]), axis=0 ) 
    shape_normal  = tf.concat ( (shape_in[:-1], [self.cfg['n_normal']]), axis=0 ) 

    return tf.concat ( (
          X, 
          tf.random.uniform (shape = shape_uniform), 
          tf.random.normal  (shape = shape_normal), 
        ), 
        axis = -1 
      )

  def get_config ( self ):
    """
      Return the configuration dictionary of this layer to allow 
      serialization. 
    """
    full_cfg = tf.keras.layers.Layer.get_config (self)
    full_cfg . update ( self.cfg ) 
    return full_cfg 

  @classmethod
  def from_config ( cls, cfg ):
    """
      Creates the layer from config. Used for deserialization. 
    """
    return cls(**cfg) 

  def compute_output_shape ( self, input_shape ):
    output_shape = list ( input_shape ) 
    output_shape[-1] += self.cfg['n_uniform'] + self.cfg['n_normal'] 
    return tuple(output_shape)