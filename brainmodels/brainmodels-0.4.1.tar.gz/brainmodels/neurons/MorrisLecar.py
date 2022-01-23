# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from .base import Neuron

__all__ = [
  'MorrisLecar'
]


class MorrisLecar(Neuron):
  r"""The Morris-Lecar neuron model.

  **Model Descriptions**

  The Morris-Lecar model [1]_ (Also known as :math:`I_{Ca}+I_K`-model)
  is a two-dimensional "reduced" excitation model applicable to
  systems having two non-inactivating voltage-sensitive conductances.
  This model was named after Cathy Morris and Harold Lecar, who
  derived it in 1981. Because it is two-dimensional, the Morris-Lecar
  model is one of the favorite conductance-based models in computational neuroscience.

  The original form of the model employed an instantaneously
  responding voltage-sensitive Ca2+ conductance for excitation and a delayed
  voltage-dependent K+ conductance for recovery. The equations of the model are:

  .. math::

      \begin{aligned}
      C\frac{dV}{dt} =& -  g_{Ca} M_{\infty} (V - V_{Ca})- g_{K} W(V - V_{K}) -
                        g_{Leak} (V - V_{Leak}) + I_{ext} \\
      \frac{dW}{dt} =& \frac{W_{\infty}(V) - W}{ \tau_W(V)}
      \end{aligned}

  Here, :math:`V` is the membrane potential, :math:`W` is the "recovery variable",
  which is almost invariably the normalized :math:`K^+`-ion conductance, and
  :math:`I_{ext}` is the applied current stimulus.

  **Model Examples**

  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>>
    >>> group = brainmodels.neurons.MorrisLecar(1)
    >>> runner = bp.StructRunner(group, monitors=['V', 'W'], inputs=('input', 100.))
    >>> runner.run(1000)
    >>>
    >>> fig, gs = bp.visualize.get_figure(2, 1, 3, 8)
    >>> fig.add_subplot(gs[0, 0])
    >>> bp.visualize.line_plot(runner.mon.ts, runner.mon.W, ylabel='W')
    >>> fig.add_subplot(gs[1, 0])
    >>> bp.visualize.line_plot(runner.mon.ts, runner.mon.V, ylabel='V', show=True)


  **Model Parameters**

  ============= ============== ======== =======================================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- -------------------------------------------------------
  V_Ca          130            mV       Equilibrium potentials of Ca+.(mV)
  g_Ca          4.4            \        Maximum conductance of corresponding Ca+.(mS/cm2)
  V_K           -84            mV       Equilibrium potentials of K+.(mV)
  g_K           8              \        Maximum conductance of corresponding K+.(mS/cm2)
  V_Leak        -60            mV       Equilibrium potentials of leak current.(mV)
  g_Leak        2              \        Maximum conductance of leak current.(mS/cm2)
  C             20             \        Membrane capacitance.(uF/cm2)
  V1            -1.2           \        Potential at which M_inf = 0.5.(mV)
  V2            18             \        Reciprocal of slope of voltage dependence of M_inf.(mV)
  V3            2              \        Potential at which W_inf = 0.5.(mV)
  V4            30             \        Reciprocal of slope of voltage dependence of W_inf.(mV)
  phi           0.04           \        A temperature factor. (1/s)
  V_th          10             mV       The spike threshold.
  ============= ============== ======== =======================================================

  **Model Variables**

  ================== ================= =========================================================
  **Variables name** **Initial Value** **Explanation**
  ------------------ ----------------- ---------------------------------------------------------
  V                  -20               Membrane potential.
  W                  0.02              Gating variable, refers to the fraction of
                                       opened K+ channels.
  input              0                 External and synaptic input current.
  spike              False             Flag to mark whether the neuron is spiking.
  t_last_spike       -1e7              Last spike time stamp.
  ================== ================= =========================================================

  **References**

  .. [1] Meier, Stephen R., Jarrett L. Lancaster, and Joseph M. Starobin.
         "Bursting regimes in a reaction-diffusion system with action
         potential-dependent equilibrium." PloS one 10.3 (2015):
         e0122401.
  .. [2] http://www.scholarpedia.org/article/Morris-Lecar_model
  .. [3] https://en.wikipedia.org/wiki/Morris%E2%80%93Lecar_model
  """

  def __init__(self, size, V_Ca=130., g_Ca=4.4, V_K=-84., g_K=8., V_leak=-60.,
               g_leak=2., C=20., V1=-1.2, V2=18., V3=2., V4=30., phi=0.04,
               V_th=10., method='exp_auto', name=None):
    # initialization
    super(MorrisLecar, self).__init__(size=size, method=method, name=name)

    # params
    self.V_Ca = V_Ca
    self.g_Ca = g_Ca
    self.V_K = V_K
    self.g_K = g_K
    self.V_leak = V_leak
    self.g_leak = g_leak
    self.C = C
    self.V1 = V1
    self.V2 = V2
    self.V3 = V3
    self.V4 = V4
    self.phi = phi
    self.V_th = V_th

    # vars
    self.W = bm.Variable(bm.ones(self.num) * 0.02)

  def dV(self, V, t, W, Iext):
    M_inf = (1 / 2) * (1 + bm.tanh((V - self.V1) / self.V2))
    I_Ca = self.g_Ca * M_inf * (V - self.V_Ca)
    I_K = self.g_K * W * (V - self.V_K)
    I_Leak = self.g_leak * (V - self.V_leak)
    dVdt = (- I_Ca - I_K - I_Leak + Iext) / self.C
    return dVdt

  def dW(self, W, t, V):
    tau_W = 1 / (self.phi * bm.cosh((V - self.V3) / (2 * self.V4)))
    W_inf = (1 / 2) * (1 + bm.tanh((V - self.V3) / self.V4))
    dWdt = (W_inf - W) / tau_W
    return dWdt

  @property
  def derivative(self):
    return bp.JointEq([self.dV, self.dW])

  def update(self, _t, _dt):
    V, self.W.value = self.integral(self.V, self.W, _t, self.input, dt=_dt)
    spike = bm.logical_and(self.V < self.V_th, V >= self.V_th)
    self.t_last_spike.value = bm.where(spike, _t, self.t_last_spike)
    self.V.value = V
    self.spike.value = spike
    self.input[:] = 0.
