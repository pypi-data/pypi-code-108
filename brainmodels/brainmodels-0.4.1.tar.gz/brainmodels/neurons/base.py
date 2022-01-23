# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

__all__ = [
  'Neuron',
]


class Neuron(bp.NeuGroup):
  def __init__(self, size, method='exp_euler_auto', name=None):
    super(Neuron, self).__init__(size=size, name=name)

    # variables
    self.V = bm.Variable(bm.zeros(self.num))
    self.input = bm.Variable(bm.zeros(self.num))
    self.spike = bm.Variable(bm.zeros(self.num, dtype=bool))
    self.t_last_spike = bm.Variable(bm.ones(self.num) * -1e7)

    # integral
    self.integral = bp.odeint(method=method, f=self.derivative)

  def derivative(self, *args, **kwargs):
    raise NotImplementedError

  def update(self, _t, _dt):
    raise NotImplementedError
