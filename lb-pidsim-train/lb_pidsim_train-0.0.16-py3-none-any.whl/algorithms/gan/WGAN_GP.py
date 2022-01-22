#from __future__ import annotations

import tensorflow as tf
from lb_pidsim_train.algorithms.gan import GAN


d_loss_tracker = tf.keras.metrics.Mean ( name = "d_loss" )
"""Metric instance to track the discriminator loss score."""

g_loss_tracker = tf.keras.metrics.Mean ( name = "g_loss" )
"""Metric instance to track the generator loss score."""


class WGAN_GP (GAN):   # TODO add class description
  """Keras model class to build and train WGAN-GP system.
  
  Parameters
  ----------
  discriminator : `tf.keras.Sequential`
    ...

  generator : `tf.keras.Sequential`
    ...

  latent_dim : `int`, optional
    ... (`64`, by default).

  Attributes
  ----------
  discriminator : `tf.keras.Sequential`
    ...

  generator : `tf.keras.Sequential`
    ...

  latent_dim : `int`
    ...

  Notes
  -----
  ...

  References
  ----------
  ...

  See Also
  --------
  ...

  Methods
  -------
  ...
  """
  def __init__ ( self ,
                 X_shape ,
                 Y_shape ,
                 discriminator ,
                 generator     ,
                 latent_dim = 64 ) -> None:
    super().__init__ ( X_shape = X_shape ,
                       Y_shape = Y_shape ,
                       discriminator = discriminator , 
                       generator     = generator     ,
                       latent_dim    = latent_dim    )
    self._loss_name = "Wasserstein distance"

  def compile ( self , 
                d_optimizer , 
                g_optimizer ,
                d_updt_per_batch = 1 , 
                g_updt_per_batch = 1 ,
                grad_penalty = 10 ) -> None:   # TODO complete docstring
    """Configure the models for WGAN-GP training.
    
    Parameters
    ----------
    d_optimizer : `tf.keras.optimizers.Optimizer`
      ...

    g_optimizer : `tf.keras.optimizers.Optimizer`
      ...

    d_updt_per_batch : `int`, optional
      ... (`1`, by default).

    g_updt_per_batch : `int`, optional
      ... (`1`, by default).
    """
    super().compile ( d_optimizer = d_optimizer , 
                      g_optimizer = g_optimizer , 
                      d_updt_per_batch = d_updt_per_batch , 
                      g_updt_per_batch = g_updt_per_batch )

    ## Data-type control
    try:
      grad_penalty = float ( grad_penalty )
    except:
      raise TypeError ("The loss gradient penalty should be a float.")

    self._grad_penalty = grad_penalty

  def _compute_d_loss (self, gen_sample, ref_sample) -> tf.Tensor:   # TODO complete docstring
    """Return the discriminator loss.
    
    Parameters
    ----------
    gen_sample : `tuple` of `tf.Tensor`
      ...

    ref_sample : `tuple` of `tf.Tensor`
      ...

    Returns
    -------
    g_loss : `tf.Tensor`
      ...
    """
    ## Extract input tensors and weights
    XY_gen, w_gen = gen_sample
    XY_ref, w_ref = ref_sample

    ## Standard WGAN loss
    D_gen = self._discriminator ( XY_gen )
    D_ref = self._discriminator ( XY_ref )
    d_loss = w_gen * D_gen - w_ref * D_ref
    
    ## Gradient penalty
    alpha = tf.random.uniform (
                                shape  = (tf.shape(XY_ref)[0], 1) ,
                                minval = 0.0 ,
                                maxval = 1.0 ,
                              )
    differences  = XY_gen - XY_ref
    interpolates = XY_ref + alpha * differences
    D_int = self._discriminator ( interpolates )
    grad = tf.gradients ( D_int , interpolates )
    grad = tf.concat  ( grad , axis = 1 )
    grad = tf.reshape ( grad , shape = (tf.shape(grad)[0], -1) )
    slopes  = tf.norm ( grad , axis = 1 )
    gp_term = tf.square ( tf.maximum ( tf.abs (slopes) - 1.0, 0.0 ) )
    gp_term = self._grad_penalty * tf.reduce_mean (gp_term)
    d_loss += gp_term
    return d_loss

  def _compute_g_loss (self, gen_sample, ref_sample) -> tf.Tensor:   # TODO complete docstring
    """Return the generator loss.
    
    Parameters
    ----------
    gen_sample : `tuple` of `tf.Tensor`
      ...

    ref_sample : `tuple` of `tf.Tensor`
      ...

    Returns
    -------
    g_loss : `tf.Tensor`
      ...
    """
    ## Extract input tensors and weights
    XY_gen, w_gen = gen_sample
    XY_ref, w_ref = ref_sample

    ## Standard WGAN loss
    D_gen = self._discriminator ( XY_gen )
    D_ref = self._discriminator ( XY_ref )
    g_loss = w_ref * D_ref - w_gen * D_gen
    return tf.reduce_mean (g_loss)

  def _compute_threshold (self, ref_sample) -> tf.Tensor:
    """Return the threshold for loss values.
    
    Parameters
    ----------
    ref_sample : `tuple` of `tf.Tensor`
      ...

    Returns
    -------
    th_loss : `tf.Tensor`
      ...
    """
    XY_ref, w_ref = ref_sample
    th_loss = tf.zeros_like (w_ref)
    return tf.reduce_mean (th_loss)

  @property
  def discriminator (self) -> tf.keras.Sequential:
    """The discriminator of the WGAN-GP system."""
    return self._discriminator

  @property
  def generator (self) -> tf.keras.Sequential:
    """The generator of the WGAN-GP system."""
    return self._generator
