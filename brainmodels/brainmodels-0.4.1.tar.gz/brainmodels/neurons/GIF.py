# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

from .base import Neuron

__all__ = [
  'GIF'
]


class GIF(Neuron):
  r"""Generalized Integrate-and-Fire model.

  **Model Descriptions**

  The generalized integrate-and-fire model [1]_ is given by

  .. math::

      &\frac{d I_j}{d t} = - k_j I_j

      &\frac{d V}{d t} = ( - (V - V_{rest}) + R\sum_{j}I_j + RI) / \tau

      &\frac{d V_{th}}{d t} = a(V - V_{rest}) - b(V_{th} - V_{th\infty})

  When :math:`V` meet :math:`V_{th}`, Generalized IF neuron fires:

  .. math::

      &I_j \leftarrow R_j I_j + A_j

      &V \leftarrow V_{reset}

      &V_{th} \leftarrow max(V_{th_{reset}}, V_{th})

  Note that :math:`I_j` refers to arbitrary number of internal currents.

  **Model Examples**

  - `Detailed examples to reproduce different firing patterns <https://brainpy-examples.readthedocs.io/en/latest/neurons/Niebur_2009_GIF.html>`_

  **Model Parameters**

  ============= ============== ======== ====================================================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- --------------------------------------------------------------------
  V_rest        -70            mV       Resting potential.
  V_reset       -70            mV       Reset potential after spike.
  V_th_inf      -50            mV       Target value of threshold potential :math:`V_{th}` updating.
  V_th_reset    -60            mV       Free parameter, should be larger than :math:`V_{reset}`.
  R             20             \        Membrane resistance.
  tau           20             ms       Membrane time constant. Compute by :math:`R * C`.
  a             0              \        Coefficient describes the dependence of
                                        :math:`V_{th}` on membrane potential.
  b             0.01           \        Coefficient describes :math:`V_{th}` update.
  k1            0.2            \        Constant pf :math:`I1`.
  k2            0.02           \        Constant of :math:`I2`.
  R1            0              \        Free parameter.
                                        Describes dependence of :math:`I_1` reset value on
                                        :math:`I_1` value before spiking.
  R2            1              \        Free parameter.
                                        Describes dependence of :math:`I_2` reset value on
                                        :math:`I_2` value before spiking.
  A1            0              \        Free parameter.
  A2            0              \        Free parameter.
  ============= ============== ======== ====================================================================

  **Model Variables**

  ================== ================= =========================================================
  **Variables name** **Initial Value** **Explanation**
  ------------------ ----------------- ---------------------------------------------------------
  V                  -70               Membrane potential.
  input              0                 External and synaptic input current.
  spike              False             Flag to mark whether the neuron is spiking.
  V_th               -50               Spiking threshold potential.
  I1                 0                 Internal current 1.
  I2                 0                 Internal current 2.
  t_last_spike       -1e7              Last spike time stamp.
  ================== ================= =========================================================

  **References**

  .. [1] Mihalaş, Ştefan, and Ernst Niebur. "A generalized linear
         integrate-and-fire neural model produces diverse spiking
         behaviors." Neural computation 21.3 (2009): 704-718.
  .. [2] Teeter, Corinne, Ramakrishnan Iyer, Vilas Menon, Nathan
         Gouwens, David Feng, Jim Berg, Aaron Szafer et al. "Generalized
         leaky integrate-and-fire models classify multiple neuron types."
         Nature communications 9, no. 1 (2018): 1-15.
  """

  def __init__(self, size, V_rest=-70., V_reset=-70., V_th_inf=-50., V_th_reset=-60.,
               R=20., tau=20., a=0., b=0.01, k1=0.2, k2=0.02, R1=0., R2=1., A1=0.,
               A2=0., method='exp_auto', name=None):
    # initialization
    super(GIF, self).__init__(size=size, method=method, name=name)

    # params
    self.V_rest = V_rest
    self.V_reset = V_reset
    self.V_th_inf = V_th_inf
    self.V_th_reset = V_th_reset
    self.R = R
    self.tau = tau
    self.a = a
    self.b = b
    self.k1 = k1
    self.k2 = k2
    self.R1 = R1
    self.R2 = R2
    self.A1 = A1
    self.A2 = A2

    # variables
    self.I1 = bm.Variable(bm.zeros(self.num))
    self.I2 = bm.Variable(bm.zeros(self.num))
    self.V_th = bm.Variable(bm.ones(self.num) * -50.)

  def dI1(self, I1, t):
    return - self.k1 * I1

  def dI2(self, I2, t):
    return - self.k2 * I2

  def dVth(self, V_th, t, V):
    return self.a * (V - self.V_rest) - self.b * (V_th - self.V_th_inf)

  def dV(self, V, t, I1, I2, Iext):
    return (- (V - self.V_rest) + self.R * Iext + self.R * I1 + self.R * I2) / self.tau

  @property
  def derivative(self):
    return bp.JointEq([self.dI1, self.dI2, self.dVth, self.dV])

  def update(self, _t, _dt):
    I1, I2, V_th, V = self.integral(self.I1, self.I2, self.V_th, self.V, _t, self.input, dt=_dt)
    spike = self.V_th <= V
    V = bm.where(spike, self.V_reset, V)
    I1 = bm.where(spike, self.R1 * I1 + self.A1, I1)
    I2 = bm.where(spike, self.R2 * I2 + self.A2, I2)
    reset_th = bm.logical_and(V_th < self.V_th_reset, spike)
    V_th = bm.where(reset_th, self.V_th_reset, V_th)
    self.spike.value = spike
    self.I1.value = I1
    self.I2.value = I2
    self.V_th.value = V_th
    self.V.value = V
    self.input[:] = 0.
