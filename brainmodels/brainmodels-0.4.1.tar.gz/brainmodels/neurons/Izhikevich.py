# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from .base import Neuron

__all__ = [
  'Izhikevich'
]


class Izhikevich(Neuron):
  r"""The Izhikevich neuron model.

  **Model Descriptions**

  The dynamics of the Izhikevich neuron model [1]_ [2]_ is given by:

  .. math ::

      \frac{d V}{d t} &= 0.04 V^{2}+5 V+140-u+I

      \frac{d u}{d t} &=a(b V-u)

  .. math ::

      \text{if}  v \geq 30  \text{mV}, \text{then}
      \begin{cases} v \leftarrow c \\
      u \leftarrow u+d \end{cases}

  **Model Examples**

  - `Detailed examples to reproduce different firing patterns <https://brainpy-examples.readthedocs.io/en/latest/neurons/Izhikevich_2003_Izhikevich_model.html>`_

  **Model Parameters**

  ============= ============== ======== ================================================================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- --------------------------------------------------------------------------------
  a             0.02           \        It determines the time scale of
                                        the recovery variable :math:`u`.
  b             0.2            \        It describes the sensitivity of the
                                        recovery variable :math:`u` to
                                        the sub-threshold fluctuations of the
                                        membrane potential :math:`v`.
  c             -65            \        It describes the after-spike reset value
                                        of the membrane potential :math:`v` caused by
                                        the fast high-threshold :math:`K^{+}`
                                        conductance.
  d             8              \        It describes after-spike reset of the
                                        recovery variable :math:`u`
                                        caused by slow high-threshold
                                        :math:`Na^{+}` and :math:`K^{+}` conductance.
  tau_ref       0              ms       Refractory period length. [ms]
  V_th          30             mV       The membrane potential threshold.
  ============= ============== ======== ================================================================================

  **Model Variables**

  ================== ================= =========================================================
  **Variables name** **Initial Value** **Explanation**
  ------------------ ----------------- ---------------------------------------------------------
  V                          -65        Membrane potential.
  u                          1          Recovery variable.
  input                      0          External and synaptic input current.
  spike                      False      Flag to mark whether the neuron is spiking.
  refractory                False       Flag to mark whether the neuron is in refractory period.
  t_last_spike               -1e7       Last spike time stamp.
  ================== ================= =========================================================

  **References**

  .. [1] Izhikevich, Eugene M. "Simple model of spiking neurons." IEEE
         Transactions on neural networks 14.6 (2003): 1569-1572.

  .. [2] Izhikevich, Eugene M. "Which model to use for cortical spiking neurons?."
         IEEE transactions on neural networks 15.5 (2004): 1063-1070.
  """

  def __init__(self, size, a=0.02, b=0.20, c=-65., d=8., tau_ref=0.,
               V_th=30., method='exp_auto', name=None):
    # initialization
    super(Izhikevich, self).__init__(size=size, method=method, name=name)

    # params
    self.a = a
    self.b = b
    self.c = c
    self.d = d
    self.V_th = V_th
    self.tau_ref = tau_ref

    # vars
    self.u = bm.Variable(bm.ones(self.num))
    self.refractory = bm.Variable(bm.zeros(self.num, dtype=bool))

  def dV(self, V, t, u, Iext):
    return 0.04 * V * V + 5 * V + 140 - u + Iext

  def du(self, u, t, V):
    return self.a * (self.b * V - u)

  @property
  def derivative(self):
    return bp.JointEq([self.dV, self.du])

  def update(self, _t, _dt):
    V, u = self.integral(self.V, self.u, _t, self.input, dt=_dt)
    refractory = (_t - self.t_last_spike) <= self.tau_ref
    V = bm.where(refractory, self.V, V)
    spike = self.V_th <= V
    self.t_last_spike.value = bm.where(spike, _t, self.t_last_spike)
    self.V.value = bm.where(spike, self.c, V)
    self.u.value = bm.where(spike, u + self.d, u)
    self.refractory.value = bm.logical_or(refractory, spike)
    self.spike.value = spike
    self.input[:] = 0.
