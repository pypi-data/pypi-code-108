# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from brainmodels.neurons.base import Neuron

__all__ = [
  'Synapse'
]


class Synapse(bp.TwoEndConn):
  def __init__(self, pre, post, conn, method='exp_auto', build_integral=True, **kwargs):
    super(Synapse, self).__init__(pre=pre, post=post, conn=conn, **kwargs)

    if not isinstance(pre, Neuron):
      raise bp.errors.BrainPyError(f'"pre" must be an instance of {Neuron}.')
    if not isinstance(post, Neuron):
      raise bp.errors.BrainPyError(f'"post" must be an instance of {Neuron}.')
    self.pre = pre
    self.post = post

    # integrals
    if build_integral:
      self.integral = bp.odeint(method=method, f=self.derivative)

  def derivative(self, *args, **kwargs):
    raise NotImplementedError
