# -*- coding: utf-8 -*-

import brainpy.math as bm

from .base import Neuron

__all__ = [
  'LIF'
]


class LIF(Neuron):
  r"""Leaky integrate-and-fire neuron model.

  **Model Descriptions**

  The formal equations of a LIF model [1]_ is given by:

  .. math::

      \tau \frac{dV}{dt} = - (V(t) - V_{rest}) + I(t) \\
      \text{after} \quad V(t) \gt V_{th}, V(t) = V_{reset} \quad
      \text{last} \quad \tau_{ref} \quad  \text{ms}

  where :math:`V` is the membrane potential, :math:`V_{rest}` is the resting
  membrane potential, :math:`V_{reset}` is the reset membrane potential,
  :math:`V_{th}` is the spike threshold, :math:`\tau` is the time constant,
  :math:`\tau_{ref}` is the refractory time period,
  and :math:`I` is the time-variant synaptic inputs.

  **Model Examples**

  - `(Brette, Romain. 2004) LIF phase locking <https://brainpy-examples.readthedocs.io/en/latest/neurons/Romain_2004_LIF_phase_locking.html>`_

  .. plot::
    :include-source: True

    >>> import brainmodels
    >>> import brainpy as bp
    >>>
    >>> group = brainmodels.neurons.LIF(1)
    >>>
    >>> runner = bp.StructRunner(group, monitors=['V'], inputs=('input', 26.))
    >>> runner.run(duration=200.)
    >>> bp.visualize.line_plot(runner.mon.ts, runner.mon.V, legend='0-200 ms', show=True)


  **Model Parameters**

  ============= ============== ======== =========================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- -----------------------------------------
  V_rest         0              mV       Resting membrane potential.
  V_reset        -5             mV       Reset potential after spike.
  V_th           20             mV       Threshold potential of spike.
  tau            10             ms       Membrane time constant. Compute by R * C.
  tau_ref       5              ms       Refractory period length.(ms)
  ============= ============== ======== =========================================

  **Neuron Variables**

  ================== ================= =========================================================
  **Variables name** **Initial Value** **Explanation**
  ------------------ ----------------- ---------------------------------------------------------
  V                    0                Membrane potential.
  input                0                External and synaptic input current.
  spike                False             Flag to mark whether the neuron is spiking.
  refractory           False             Flag to mark whether the neuron is in refractory period.
  t_last_spike         -1e7              Last spike time stamp.
  ================== ================= =========================================================

  **References**

  .. [1] Abbott, Larry F. "Lapicque’s introduction of the integrate-and-fire model
         neuron (1907)." Brain research bulletin 50, no. 5-6 (1999): 303-304.
  """

  def __init__(self, size, V_rest=0., V_reset=-5., V_th=20., tau=10.,
               tau_ref=1., method='exp_auto', name=None):
    # initialization
    super(LIF, self).__init__(size=size, method=method, name=name)

    # parameters
    self.V_rest = V_rest
    self.V_reset = V_reset
    self.V_th = V_th
    self.tau = tau
    self.tau_ref = tau_ref

    # variables
    self.refractory = bm.Variable(bm.zeros(self.num, dtype=bool))

  def derivative(self, V, t, Iext):
    dvdt = (-V + self.V_rest + Iext) / self.tau
    return dvdt

  def update(self, _t, _dt):
    refractory = (_t - self.t_last_spike) <= self.tau_ref
    V = self.integral(self.V, _t, self.input, dt=_dt)
    V = bm.where(refractory, self.V, V)
    spike = self.V_th <= V
    self.t_last_spike.value = bm.where(spike, _t, self.t_last_spike)
    self.V.value = bm.where(spike, self.V_reset, V)
    self.refractory.value = bm.logical_or(refractory, spike)
    self.spike.value = spike
    self.input[:] = 0.
