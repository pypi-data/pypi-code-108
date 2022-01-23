# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

from .base import Synapse

__all__ = [
  'VoltageJump',
  'DeltaSynapse',
]


class DeltaSynapse(Synapse):
  """Voltage Jump Synapse Model, or alias of Delta Synapse Model.

  **Model Descriptions**

  .. math::

      I_{syn} (t) = \sum_{j\in C} w \delta(t-t_j-D)

  where :math:`w` denotes the chemical synaptic strength, :math:`t_j` the spiking
  moment of the presynaptic neuron :math:`j`, :math:`C` the set of neurons connected
  to the post-synaptic neuron, and :math:`D` the transmission delay of chemical
  synapses. For simplicity, the rise and decay phases of post-synaptic currents are
  omitted in this model.

  **Model Examples**

  - `(Bouchacourt & Buschman, 2019) Flexible Working Memory Model <https://brainpy-examples.readthedocs.io/en/latest/working_memory/Bouchacourt_2019_Flexible_working_memory.html>`_

  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>> import matplotlib.pyplot as plt
    >>>
    >>> neu1 = brainmodels.neurons.LIF(1)
    >>> neu2 = brainmodels.neurons.LIF(1)
    >>> syn1 = brainmodels.synapses.DeltaSynapse(neu1, neu2, bp.connect.All2All(), w=5.)
    >>> net = bp.Network(pre=neu1, syn=syn1, post=neu2)
    >>>
    >>> runner = bp.StructRunner(net, inputs=[('pre.input', 25.), ('post.input', 10.)], monitors=['pre.V', 'post.V', 'pre.spike'])
    >>> runner.run(150.)
    >>>
    >>>
    >>> fig, gs = bp.visualize.get_figure(1, 1, 3, 8)
    >>> plt.plot(runner.mon.ts, runner.mon['pre.V'], label='pre-V')
    >>> plt.plot(runner.mon.ts, runner.mon['post.V'], label='post-V')
    >>> plt.xlim(40, 150)
    >>> plt.legend()
    >>> plt.show()


  **Model Parameters**

  ============= ============== ======== ===========================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- -------------------------------------------
  w             1              mV       The synaptic strength.
  ============= ============== ======== ===========================================

  """

  def __init__(self, pre, post, conn, delay=0., post_has_ref=False, w=1., post_key='V', name=None):
    super(DeltaSynapse, self).__init__(pre=pre, post=post, conn=conn, build_integral=False, name=name)
    self.check_pre_attrs('spike')
    self.check_post_attrs(post_key)
    if post_has_ref:
      self.check_post_attrs('refractory')

    # parameters
    self.delay = delay
    self.post_key = post_key
    self.post_has_ref = post_has_ref

    # connections
    self.pre2post = self.conn.require('pre2post')

    # variables
    self.w = w
    self.pre_spike = bp.ConstantDelay(pre.num, delay, dtype=pre.spike.dtype)

  def update(self, _t, _dt):
    self.pre_spike.push(self.pre.spike)
    delayed_pre_spike = self.pre_spike.pull()
    post_vs = bm.pre2post_event_sum(delayed_pre_spike, self.pre2post, self.post.num, self.w)
    target = getattr(self.post, self.post_key)
    if self.post_has_ref:
      target += post_vs * (1. - self.post.refractory)
    else:
      target += post_vs


class VoltageJump(DeltaSynapse):
  def __init__(self, pre, post, conn, delay=0., post_has_ref=False, w=1., name=None):
    super(VoltageJump, self).__init__(pre=pre, post=post, conn=conn, delay=delay,
                                      post_has_ref=post_has_ref, w=w, name=name)


