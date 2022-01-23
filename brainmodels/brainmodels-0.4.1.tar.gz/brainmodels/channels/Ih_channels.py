# -*- coding: utf-8 -*-


import brainpy as bp
import brainpy.math as bm
from .base import IonChannel

__all__ = [
  'Ih',
]


class Ih(IonChannel):
  r"""The hyperpolarization-activated cation current model.

  The hyperpolarization-activated cation current model is adopted from (Huguenard, et, al., 1992) [1]_.
  Its dynamics is given by:

  .. math::

      \begin{aligned}
      I_h &= g_{\mathrm{max}} p
      \\
      \frac{dp}{dt} &= \phi \frac{p_{\infty} - p}{\tau_p}
      \\
      p_{\infty} &=\frac{1}{1+\exp ((V+75) / 5.5)}
      \\
      \tau_{p} &=\frac{1}{\exp (-0.086 V-14.59)+\exp (0.0701 V-1.87)}
      \end{aligned}

  where :math:`\phi=1` is a temperature-dependent factor.

  Parameters
  ----------
  g_max : float
    The maximal conductance density (:math:`mS/cm^2`).
  E : float
    The reversal potential (mV).
  phi : float
    The temperature-dependent factor.

  References
  ----------
  .. [1] Huguenard, John R., and David A. McCormick. "Simulation of the currents
         involved in rhythmic oscillations in thalamic relay neurons." Journal
         of neurophysiology 68, no. 4 (1992): 1373-1383.

  """
  allowed_params = ('g_max', 'E', 'phi')

  def __init__(self, host, method, g_max=10., E=-90., phi=1., name=None):
    super(Ih, self).__init__(host, method, name=name)

    self.phi = phi
    self.g_max = g_max
    self.E = E

    self.p = bm.Variable(bm.zeros(host.shape, dtype=bm.float_))

  def derivative(self, p, t, V):
    p_inf = 1. / (1. + bm.exp((V + 75.) / 5.5))
    p_tau = 1. / (bm.exp(-0.086 * V - 14.59) + bm.exp(0.0701 * V - 1.87))
    dpdt = self.phi * (p_inf - p) / p_tau
    return dpdt

  def update(self, _t, _dt):
    self.p.value = self.integral(self.p.value, _t, self.host.V.value, dt=_dt)

  def current(self):
    g = self.g_max * self.p.value
    return g * (self.E - self.host.V.value)
