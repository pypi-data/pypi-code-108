# -*- coding: utf-8 -*-

from .AMPA import AMPA

__all__ = [
  'GABAa',
]


class GABAa(AMPA):
  r"""GABAa conductance-based synapse model.

  **Model Descriptions**

  GABAa synapse model has the same equation with the `AMPA synapse <./brainmodels.synapses.AMPA.rst>`_, 
  
  .. math::

      \frac{d g}{d t}&=\alpha[T](1-g) - \beta g \\
      I_{syn}&= - g_{max} g (V - E)

  but with the difference of:

  - Reversal potential of synapse :math:`E` is usually low, typically -80. mV
  - Activating rate constant :math:`\alpha=0.53`
  - De-activating rate constant :math:`\beta=0.18`
  - Transmitter concentration :math:`[T]=1\,\mu ho(\mu S)` when synapse is
    triggered by a pre-synaptic spike, with the duration of 1. ms.

  **Model Examples**

  - `Gamma oscillation network model <https://brainpy-examples.readthedocs.io/en/latest/oscillation_synchronization/Wang_1996_gamma_oscillation.html>`_

  **Model Parameters**

  ============= ============== ======== =======================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- ---------------------------------------
  delay         0              ms       The decay length of the pre-synaptic spikes.
  g_max         0.04           µmho(µS) Maximum synapse conductance.
  E             -80            mV       Reversal potential of synapse.
  alpha         0.53           \        Activating rate constant of G protein catalyzed by activated GABAb receptor.
  beta          0.18           \        De-activating rate constant of G protein.
  T             1              mM       Transmitter concentration when synapse is triggered by a pre-synaptic spike.
  T_duration    1              ms       Transmitter concentration duration time after being triggered.
  ============= ============== ======== =======================================

  **Model Variables**

  ================== ================== ==================================================
  **Member name**    **Initial values** **Explanation**
  ------------------ ------------------ --------------------------------------------------
  g                  0                  Synapse gating variable.
  pre_spike          False              The history of pre-synaptic neuron spikes.
  spike_arrival_time -1e7               The arrival time of the pre-synaptic neuron spike.
  ================== ================== ==================================================

  **References**

  .. [1] Destexhe, Alain, and Denis Paré. "Impact of network activity
         on the integrative properties of neocortical pyramidal neurons
         in vivo." Journal of neurophysiology 81.4 (1999): 1531-1547.
  """

  def __init__(self, pre, post, conn, delay=0., g_max=0.04, E=-80., alpha=0.53,
               beta=0.18, T=1., T_duration=1., method='exp_auto', name=None):
    super(GABAa, self).__init__(pre, post, conn,
                                delay=delay,
                                g_max=g_max,
                                E=E,
                                alpha=alpha,
                                beta=beta,
                                T=T,
                                T_duration=T_duration,
                                method=method,
                                name=name)
