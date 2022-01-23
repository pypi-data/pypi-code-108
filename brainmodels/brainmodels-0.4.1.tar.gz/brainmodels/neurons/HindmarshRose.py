# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from .base import Neuron

__all__ = [
  'HindmarshRose'
]


class HindmarshRose(Neuron):
  r"""Hindmarsh-Rose neuron model.

  **Model Descriptions**

  The Hindmarsh–Rose model [1]_ [2]_ of neuronal activity is aimed to study the 
  spiking-bursting behavior of the membrane potential observed in experiments
  made with a single neuron.

  The model has the mathematical form of a system of three nonlinear ordinary 
  differential equations on the dimensionless dynamical variables :math:`x(t)`,
  :math:`y(t)`, and :math:`z(t)`. They read:

  .. math::

     \begin{aligned}
     \frac{d V}{d t} &= y - a V^3 + b V^2 - z + I \\
     \frac{d y}{d t} &= c - d V^2 - y \\
     \frac{d z}{d t} &= r (s (V - V_{rest}) - z)
     \end{aligned}

  where :math:`a, b, c, d` model the working of the fast ion channels,
  :math:`I` models the slow ion channels.

  **Model Examples**

  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>> import matplotlib.pyplot as plt
    >>>
    >>> bp.math.set_dt(dt=0.01)
    >>> bp.set_default_odeint('rk4')
    >>>
    >>> types = ['quiescence', 'spiking', 'bursting', 'irregular_spiking', 'irregular_bursting']
    >>> bs = bp.math.array([1.0, 3.5, 2.5, 2.95, 2.8])
    >>> Is = bp.math.array([2.0, 5.0, 3.0, 3.3, 3.7])
    >>>
    >>> # define neuron type
    >>> group = brainmodels.neurons.HindmarshRose(len(types), b=bs)
    >>> runner = bp.StructRunner(group, monitors=['V'], inputs=['input', Is],)
    >>> runner.run(1e3)
    >>>
    >>> fig, gs = bp.visualize.get_figure(row_num=3, col_num=2, row_len=3, col_len=5)
    >>> for i, mode in enumerate(types):
    >>>     fig.add_subplot(gs[i // 2, i % 2])
    >>>     plt.plot(runner.mon.ts, runner.mon.V[:, i])
    >>>     plt.title(mode)
    >>>     plt.xlabel('Time [ms]')
    >>> plt.show()

  **Model Parameters**

  ============= ============== ========= ============================================================
  **Parameter** **Init Value** **Unit**  **Explanation**
  ------------- -------------- --------- ------------------------------------------------------------
  a             1              \         Model parameter.
                                         Fixed to a value best fit neuron activity.
  b             3              \         Model parameter.
                                         Allows the model to switch between bursting
                                         and spiking, controls the spiking frequency.
  c             1              \         Model parameter.
                                         Fixed to a value best fit neuron activity.
  d             5              \         Model parameter.
                                         Fixed to a value best fit neuron activity.
  r             0.01           \         Model parameter.
                                         Controls slow variable z's variation speed.
                                         Governs spiking frequency when spiking, and affects the
                                         number of spikes per burst when bursting.
  s             4              \         Model parameter. Governs adaption.
  ============= ============== ========= ============================================================

  **Model Variables**

  =============== ================= =====================================
  **Member name** **Initial Value** **Explanation**
  --------------- ----------------- -------------------------------------
  V               -1.6              Membrane potential.
  y               -10               Gating variable.
  z               0                 Gating variable.
  spike           False             Whether generate the spikes.
  input           0                 External and synaptic input current.
  t_last_spike    -1e7              Last spike time stamp.
  =============== ================= =====================================

  **References**

  .. [1] Hindmarsh, James L., and R. M. Rose. "A model of neuronal bursting using
        three coupled first order differential equations." Proceedings of the
        Royal society of London. Series B. Biological sciences 221.1222 (1984):
        87-102.
  .. [2] Storace, Marco, Daniele Linaro, and Enno de Lange. "The Hindmarsh–Rose
        neuron model: bifurcation analysis and piecewise-linear approximations."
        Chaos: An Interdisciplinary Journal of Nonlinear Science 18.3 (2008):
        033128.
  """

  def __init__(self, size, a=1., b=3., c=1., d=5., r=0.01, s=4., V_rest=-1.6,
               V_th=1.0, method='exp_auto', name=None):
    # initialization
    super(HindmarshRose, self).__init__(size=size, method=method, name=name)

    # parameters
    self.a = a
    self.b = b
    self.c = c
    self.d = d
    self.r = r
    self.s = s
    self.V_th = V_th
    self.V_rest = V_rest

    # variables
    self.z = bm.Variable(bm.zeros(self.num))
    self.y = bm.Variable(bm.ones(self.num) * -10.)

  def dV(self, V, t, y, z, Iext):
    return y - self.a * V * V * V + self.b * V * V - z + Iext

  def dy(self, y, t, V):
    return self.c - self.d * V * V - y

  def dz(self, z, t, V):
    return self.r * (self.s * (V - self.V_rest) - z)

  @property
  def derivative(self):
    return bp.JointEq([self.dV, self.dy, self.dz])

  def update(self, _t, _dt):
    V, y, z = self.integral(self.V, self.y, self.z, _t, self.input, dt=_dt)
    self.spike.value = bm.logical_and(V >= self.V_th, self.V < self.V_th)
    self.t_last_spike.value = bm.where(self.spike, _t, self.t_last_spike)
    self.V.value = V
    self.y.value = y
    self.z.value = z
    self.input[:] = 0.
