# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from .base import Synapse

__all__ = [
  'NMDA'
]


class NMDA(Synapse):
  r"""Conductance-based NMDA synapse model.

  **Model Descriptions**

  The NMDA receptor is a glutamate receptor and ion channel found in neurons.
  The NMDA receptor is one of three types of ionotropic glutamate receptors,
  the other two being AMPA and kainate receptors.

  The NMDA receptor mediated conductance depends on the postsynaptic voltage.
  The voltage dependence is due to the blocking of the pore of the NMDA receptor
  from the outside by a positively charged magnesium ion. The channel is
  nearly completely blocked at resting potential, but the magnesium block is
  relieved if the cell is depolarized. The fraction of channels :math:`g_{\infty}`
  that are not blocked by magnesium can be fitted to
  
  .. math::
      
      g_{\infty}(V,[{Mg}^{2+}]_{o}) = (1+{e}^{-\alpha V}
      \frac{[{Mg}^{2+}]_{o}} {\beta})^{-1} 

  Here :math:`[{Mg}^{2+}]_{o}` is the extracellular magnesium concentration,
  usually 1 mM. Thus, the channel acts as a
  "coincidence detector" and only once both of these conditions are met, the
  channel opens and it allows positively charged ions (cations) to flow through
  the cell membrane [2]_.

  If we make the approximation that the magnesium block changes
  instantaneously with voltage and is independent of the gating of the channel,
  the net NMDA receptor-mediated synaptic current is given by

  .. math::

      I_{syn} = g_{NMDA}(t) (V(t)-E) \cdot g_{\infty}

  where :math:`V(t)` is the post-synaptic neuron potential, :math:`E` is the
  reversal potential.

  Simultaneously, the kinetics of synaptic state :math:`g` is given by

  .. math::

      & g_{NMDA} (t) = g_{max} g \\
      & \frac{d g}{dt} = -\frac{g} {\tau_{decay}}+a x(1-g) \\
      & \frac{d x}{dt} = -\frac{x}{\tau_{rise}}+ \sum_{k} \delta(t-t_{j}^{k})

  where the decay time of NMDA currents is usually taken to be
  :math:`\tau_{decay}` =100 ms, :math:`a= 0.5 ms^{-1}`, and :math:`\tau_{rise}` =2 ms.

  The NMDA receptor has been thought to be very important for controlling
  synaptic plasticity and mediating learning and memory functions [3]_.


  **Model Examples**

  - `(Wang, 2002) Decision making spiking model <https://brainpy-examples.readthedocs.io/en/latest/decision_making/Wang_2002_decision_making_spiking.html>`_


  .. plot::
    :include-source: True

    >>> import brainpy as bp
    >>> import brainmodels
    >>> import matplotlib.pyplot as plt
    >>>
    >>> neu1 = brainmodels.neurons.HH(1)
    >>> neu2 = brainmodels.neurons.HH(1)
    >>> syn1 = brainmodels.synapses.NMDA(neu1, neu2, bp.connect.All2All(), E=0.)
    >>> net = bp.Network(pre=neu1, syn=syn1, post=neu2)
    >>>
    >>> runner = bp.StructRunner(net, inputs=[('pre.input', 5.)], monitors=['pre.V', 'post.V', 'syn.g', 'syn.x'])
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
    >>> plt.plot(runner.mon.ts, runner.mon['syn.x'], label='x')
    >>> plt.legend()
    >>> plt.show()



  **Model Parameters**

  ============= ============== =============== ================================================
  **Parameter** **Init Value** **Unit**        **Explanation**
  ------------- -------------- --------------- ------------------------------------------------
  delay         0              ms              The decay length of the pre-synaptic spikes.
  g_max         .15            µmho(µS)        The synaptic maximum conductance.
  E             0              mV              The reversal potential for the synaptic current.
  alpha         .062           \               Binding constant.
  beta          3.57           \               Unbinding constant.
  cc_Mg         1.2            mM              Concentration of Magnesium ion.
  tau_decay     100            ms              The time constant of the synaptic decay phase.
  tau_rise      2              ms              The time constant of the synaptic rise phase.
  a             .5             1/ms
  ============= ============== =============== ================================================


  **Model Variables**

  =============== ================== =========================================================
  **Member name** **Initial values** **Explanation**
  --------------- ------------------ --------------------------------------------------------- 
  g               0                  Synaptic conductance.
  x               0                  Synaptic gating variable.
  pre_spike       False              The history spiking states of the pre-synaptic neurons.
  =============== ================== =========================================================
      
  **References**
  
  .. [1] Brunel N, Wang X J. Effects of neuromodulation in a 
         cortical network model of object working memory dominated 
         by recurrent inhibition[J]. 
         Journal of computational neuroscience, 2001, 11(1): 63-85.
  .. [2] Furukawa, Hiroyasu, Satinder K. Singh, Romina Mancusso, and
         Eric Gouaux. "Subunit arrangement and function in NMDA receptors."
         Nature 438, no. 7065 (2005): 185-192.
  .. [3] Li, F. and Tsien, J.Z., 2009. Memory and the NMDA receptors. The New
         England journal of medicine, 361(3), p.302.
  .. [4] https://en.wikipedia.org/wiki/NMDA_receptor

  """

  def __init__(self, pre, post, conn, delay=0., g_max=0.15, E=0., cc_Mg=1.2,
               alpha=0.062, beta=3.57, tau_decay=100., a=0.5, tau_rise=2.,
               method='exp_auto', name=None):
    super(NMDA, self).__init__(pre=pre, post=post, conn=conn, method=method, name=name)
    self.check_pre_attrs('spike')
    self.check_post_attrs('input', 'V')

    # parameters
    self.g_max = g_max
    self.E = E
    self.alpha = alpha
    self.beta = beta
    self.cc_Mg = cc_Mg
    self.tau_decay = tau_decay
    self.tau_rise = tau_rise
    self.a = a
    self.delay = delay

    # connections
    self.pre_ids, self.post_ids = self.conn.require('pre_ids', 'post_ids')

    # variables
    num = len(self.pre_ids)
    self.pre_spike = bp.ConstantDelay(self.pre.num, delay, pre.spike.dtype)
    self.g = bm.Variable(bm.zeros(num, dtype=bm.float_))
    self.x = bm.Variable(bm.zeros(num, dtype=bm.float_))

  @property
  def derivative(self):
    dg = lambda g, t, x: -g / self.tau_decay + self.a * x * (1 - g)
    dx = lambda x, t:  -x / self.tau_rise
    return bp.JointEq([dg, dx])

  def update(self, _t, _dt):
    self.pre_spike.push(self.pre.spike)
    delayed_pre_spike = self.pre_spike.pull()
    self.g.value, self.x.value = self.integral(self.g, self.x, _t, dt=_dt)
    self.x += bm.pre2syn(delayed_pre_spike, self.pre_ids)
    post_g = bm.syn2post(self.g, self.post_ids, self.post.num)
    g_inf = 1 + self.cc_Mg / self.beta * bm.exp(-self.alpha * self.post.V)
    self.post.input -= self.g_max * post_g * (self.post.V - self.E) / g_inf
