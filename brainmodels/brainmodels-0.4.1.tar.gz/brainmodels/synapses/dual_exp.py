# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

from .base import Synapse

__all__ = [
  'DualExpCUBA', 'DualExpCOBA',
]


class DualExpCUBA(Synapse):
  r"""Current-based dual exponential synapse model.

  **Model Descriptions**

  The dual exponential synapse model [1]_, also named as *difference of two exponentials* model,
  is given by:

  .. math::

    g_{\mathrm{syn}}(t)=g_{\mathrm{max}} \frac{\tau_{1} \tau_{2}}{
        \tau_{1}-\tau_{2}}\left(\exp \left(-\frac{t-t_{0}}{\tau_{1}}\right)
        -\exp \left(-\frac{t-t_{0}}{\tau_{2}}\right)\right)

  where :math:`\tau_1` is the time constant of the decay phase, :math:`\tau_2`
  is the time constant of the rise phase, :math:`t_0` is the time of the pre-synaptic
  spike, :math:`g_{\mathrm{max}}` is the maximal conductance.

  However, in practice, this formula is hard to implement. The equivalent solution is
  two coupled linear differential equations [2]_:

  .. math::

      \begin{aligned}
      &g_{\mathrm{syn}}(t)=g_{\mathrm{max}} g \\
      &\frac{d g}{d t}=-\frac{g}{\tau_{\mathrm{decay}}}+h \\
      &\frac{d h}{d t}=-\frac{h}{\tau_{\text {rise }}}+ \delta\left(t_{0}-t\right),
      \end{aligned}

  The current onto the post-synaptic neuron is given by

  .. math::
  
      I_{syn}(t) = g_{\mathrm{syn}}(t).


  **Model Examples**


  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>> import matplotlib.pyplot as plt
    >>>
    >>> neu1 = brainmodels.neurons.LIF(1)
    >>> neu2 = brainmodels.neurons.LIF(1)
    >>> syn1 = brainmodels.synapses.DualExpCUBA(neu1, neu2, bp.connect.All2All())
    >>> net = bp.Network(pre=neu1, syn=syn1, post=neu2)
    >>>
    >>> runner = bp.StructRunner(net, inputs=[('pre.input', 25.)], monitors=['pre.V', 'post.V', 'syn.g', 'syn.h'])
    >>> runner.run(150.)
    >>>
    >>> fig, gs = bp.visualize.get_figure(2, 1, 3, 8)
    >>> fig.add_subplot(gs[0, 0])
    >>> plt.plot(runner.mon.ts, runner.mon['pre.V'], label='pre-V')
    >>> plt.plot(runner.mon.ts, runner.mon['post.V'], label='post-V')
    >>> plt.legend()
    >>>
    >>> fig.add_subplot(gs[1, 0])
    >>> plt.plot(runner.mon.ts, runner.mon['syn.g'], label='g')
    >>> plt.plot(runner.mon.ts, runner.mon['syn.h'], label='h')
    >>> plt.legend()
    >>> plt.show()


  **Model Parameters**

  ============= ============== ======== ===================================================================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- -----------------------------------------------------------------------------------
  delay         0              ms       The decay length of the pre-synaptic spikes.
  tau_decay     10             ms       The time constant of the synaptic decay phase.
  tau_rise      1              ms       The time constant of the synaptic rise phase.
  g_max         1              µmho(µS) The maximum conductance.
  ============= ============== ======== ===================================================================================


  **Model Variables**

  ================ ================== =========================================================
  **Member name**  **Initial values** **Explanation**
  ---------------- ------------------ ---------------------------------------------------------    
  g                  0                 Synapse conductance on the post-synaptic neuron.
  s                  0                 Gating variable.
  pre_spike          False             The history spiking states of the pre-synaptic neurons.
  ================ ================== =========================================================

  **References**

  .. [1] Sterratt, David, Bruce Graham, Andrew Gillies, and David Willshaw.
         "The Synapse." Principles of Computational Modelling in Neuroscience.
         Cambridge: Cambridge UP, 2011. 172-95. Print.
  .. [2] Roth, A., & Van Rossum, M. C. W. (2009). Modeling Synapses. Computational
         Modeling Methods for Neuroscientists.

  """

  def __init__(self, pre, post, conn, delay=0., g_max=1., tau_decay=10.0, tau_rise=1.,
               method='exp_auto', name=None):
    super(DualExpCUBA, self).__init__(pre=pre, post=post, conn=conn, method=method, name=name)
    self.check_pre_attrs('spike')
    self.check_post_attrs('input')

    # parameters
    self.tau_rise = tau_rise
    self.tau_decay = tau_decay
    self.delay = delay
    self.g_max = g_max

    # connections
    self.pre_ids, self.post_ids = self.conn.require('pre_ids', 'post_ids')

    # variables
    self.g = bm.Variable(bm.zeros( len(self.pre_ids)))
    self.h = bm.Variable(bm.zeros( len(self.pre_ids)))
    self.pre_spike = bp.ConstantDelay(self.pre.num, delay, dtype=pre.spike.dtype)

  @property
  def derivative(self):
    dg = lambda g, t, h: -g / self.tau_decay + h
    dh = lambda h, t: -h / self.tau_rise
    return bp.JointEq([dg, dh])

  def update(self, _t, _dt):
    self.pre_spike.push(self.pre.spike)
    delayed_pre_spikes = self.pre_spike.pull()
    self.g.value, self.h.value = self.integral(self.g, self.h, _t, dt=_dt)
    self.h.value += bm.pre2syn(delayed_pre_spikes, self.pre_ids)
    self.post.input += self.g_max * bm.syn2post(self.g, self.post_ids, self.post.num)


class DualExpCOBA(DualExpCUBA):
  """Conductance-based dual exponential synapse model.

  **Model Descriptions**

  The conductance-based dual exponential synapse model is similar with the
  `current-based dual exponential synapse model <./brainmodels.synapses.DualExpCUBA.rst>`_,
  except the expression which output onto the post-synaptic neurons:

  .. math::

      I_{syn}(t) = g_{\mathrm{syn}}(t) (V(t)-E)

  where :math:`V(t)` is the membrane potential of the post-synaptic neuron,
  :math:`E` is the reversal potential.

  **Model Examples**

  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>> import matplotlib.pyplot as plt
    >>>
    >>> neu1 = brainmodels.neurons.HH(1)
    >>> neu2 = brainmodels.neurons.HH(1)
    >>> syn1 = brainmodels.synapses.DualExpCOBA(neu1, neu2, bp.connect.All2All(), E=0.)
    >>> net = bp.Network(pre=neu1, syn=syn1, post=neu2)
    >>>
    >>> runner = bp.StructRunner(net, inputs=[('pre.input', 5.)], monitors=['pre.V', 'post.V', 'syn.g', 'syn.h'])
    >>> runner.run(150.)
    >>>
    >>> fig, gs = bp.visualize.get_figure(2, 1, 3, 8)
    >>> fig.add_subplot(gs[0, 0])
    >>> plt.plot(runner.mon.ts, runner.mon['pre.V'], label='pre-V')
    >>> plt.plot(runner.mon.ts, runner.mon['post.V'], label='post-V')
    >>> plt.legend()
    >>>
    >>> fig.add_subplot(gs[1, 0])
    >>> plt.plot(runner.mon.ts, runner.mon['syn.g'], label='g')
    >>> plt.plot(runner.mon.ts, runner.mon['syn.h'], label='h')
    >>> plt.legend()
    >>> plt.show()


  **Model Parameters**

  ============= ============== ======== ===================================================================================
  **Parameter** **Init Value** **Unit** **Explanation**
  ------------- -------------- -------- -----------------------------------------------------------------------------------
  delay         0              ms       The decay length of the pre-synaptic spikes.
  tau_decay     10             ms       The time constant of the synaptic decay phase.
  tau_rise      1              ms       The time constant of the synaptic rise phase.
  g_max         1              µmho(µS) The maximum conductance.
  E             0              mV       The reversal potential for the synaptic current.
  ============= ============== ======== ===================================================================================


  **Model Variables**

  ================ ================== =========================================================
  **Member name**  **Initial values** **Explanation**
  ---------------- ------------------ ---------------------------------------------------------
  g                  0                 Synapse conductance on the post-synaptic neuron.
  s                  0                 Gating variable.
  pre_spike          False             The history spiking states of the pre-synaptic neurons.
  ================ ================== =========================================================

  **References**

  .. [1] Sterratt, David, Bruce Graham, Andrew Gillies, and David Willshaw.
         "The Synapse." Principles of Computational Modelling in Neuroscience.
         Cambridge: Cambridge UP, 2011. 172-95. Print.

  """
  def __init__(self, pre, post, conn, delay=0., g_max=1., tau_decay=10.0, tau_rise=1.,
               E=0., method='exp_auto', name=None):
    super(DualExpCOBA, self).__init__(pre, post, conn, delay=delay, g_max=g_max,
                                      tau_decay=tau_decay, tau_rise=tau_rise,
                                      method=method, name=name)
    self.check_post_attrs('V')

    # parameters
    self.E = E

  def update(self, _t, _dt):
    self.pre_spike.push(self.pre.spike)
    delayed_pre_spikes = self.pre_spike.pull()
    self.g.value, self.h.value = self.integral(self.g, self.h, _t, dt=_dt)
    self.h.value += bm.pre2syn(delayed_pre_spikes, self.pre_ids)
    post_g = bm.syn2post(self.g, self.post_ids, self.post.num)
    self.post.input += self.g_max * post_g * (self.E - self.post.V)

