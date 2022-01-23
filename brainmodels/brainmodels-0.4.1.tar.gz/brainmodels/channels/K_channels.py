# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

from .base import IonChannel

__all__ = [
  'IDR',
  'IK2',
]


class IDR(IonChannel):
  r"""The delayed rectifier potassium channel current.

  The potassium current model is adopted from (Bazhenov, et, al. 2002) [1]_.
  It's dynamics is given by:

  .. math::

      \begin{aligned}
      I_{\mathrm{K}} &= g_{\mathrm{max}} * p^4 \\
      \frac{dp}{dt} &= \phi * (\alpha_p (1-p) - \beta_p p) \\
      \alpha_{p} &=\frac{0.032\left(V-V_{sh}-15\right)}{1-\exp \left(-\left(V-V_{sh}-15\right) / 5\right)} \\
      \beta_p &= 0.5 \exp \left(-\left(V-V_{sh}-10\right) / 40\right)
      \end{aligned}

  where :math:`\phi` is a temperature-dependent factor, which is given by
  :math:`\phi=3^{\frac{T-36}{10}}` (:math:`T` is the temperature in Celsius).

  **Model Examples**

  - `(Brette, et, al., 2007) COBAHH <../../examples/ei_nets/Brette_2007_COBAHH.ipynb>`_


  Parameters
  ----------
  g_max : float
    The maximal conductance density (:math:`mS/cm^2`).
  E : float
    The reversal potential (mV).
  T : float
    The temperature (Celsius, :math:`^{\circ}C`).
  V_sh : float
    The shift of the membrane potential to spike.

  References
  ----------
  .. [1] Bazhenov, Maxim, et al. "Model of thalamocortical slow-wave sleep oscillations
         and transitions to activated states." Journal of neuroscience 22.19 (2002): 8691-8704.

  """
  allowed_params = ('E', 'g_max', 'T', 'T_base', 'V_sh')

  def __init__(self, host, method, E=-90., g_max=10., T=36., T_base=3., V_sh=-50., name=None):
    super(IDR, self).__init__(host, method, name=name)

    # parameters
    self.T = T
    self.T_base = T_base
    self.E = E
    self.g_max = g_max
    self.V_sh = V_sh

    # variables
    self.p = bm.Variable(bm.zeros(self.host.num, dtype=bm.float_))

  def derivative(self, p, t, V):
    phi = self.T_base ** ((self.T - 36) / 10)
    alpha_p = 0.032 * (V - self.V_sh - 15.) / (1. - bm.exp(-(V - self.V_sh - 15.) / 5.))
    beta_p = 0.5 * bm.exp(-(V - self.V_sh - 10.) / 40.)
    dpdt = phi * (alpha_p * (1. - p) - beta_p * p)
    return dpdt

  def update(self, _t, _dt):
    self.p.value = self.integral(self.p.value, _t, self.host.V.value, dt=_dt)

  def current(self):
    return self.g_max * self.p.value ** 4 * (self.E - self.host.V.value)


class IK2(IonChannel):

  def __init__(self, host, method, E, g_max, name=None):
    super(IK2, self).__init__(host, method, name=name)

    self.E = E
    self.g_max = g_max

    self.n = bp.math.Variable(bp.math.zeros(host.shape, dtype=bp.math.float_))

  def derivative(self, n, t, V):
    alpha = 0.01 * (V + 55) / (1 - bp.math.exp(-(V + 55) / 10))
    beta = 0.125 * bp.math.exp(-(V + 65) / 80)
    dndt = alpha * (1 - n) - beta * n
    return dndt

  def update(self, _t, _dt):
    self.n.value = self.integral(self.n.value, _t, self.host.V.value, dt=_dt)

  def current(self):
    g = self.g_max * self.n.value ** 4
    return g * (self.E - self.host.V.value)
