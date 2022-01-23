# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm

from .base import MolChannel, CalChannel

__all__ = [
  'Ca',
  'CaFix',
  'CaDyn',

  'IAHP',
  'ICaN',
  'ICaT',
  'ICaT_RE',
  'ICaHT',
  'ICaL',
]


class Ca(MolChannel):
  """The base calcium dynamics."""
  E = None
  I_Ca = None

  def __init__(self, host, method, name=None):
    super(Ca, self).__init__(host, method, name=name)


class CaFix(Ca):
  """Fixed Calcium dynamics.

  This calcium model has no dynamics. It only hold a fixed reversal potential :math:`E`.
  """
  allowed_params = ('E',)

  def __init__(self, host, method, E=120., name=None):
    super(CaFix, self).__init__(host, method, E=E, name=name)

    self.E = E
    self.input = bm.Variable(bm.zeros(host.num, dtype=bm.float_))

  def update(self, _t, _dt):
    self.input[:] = 0.


class CaDyn(Ca):
  r"""Dynamical Calcium model.

  **1. The dynamics of intracellular** :math:`Ca^{2+}`

  The dynamics of intracellular :math:`Ca^{2+}` were determined by two contributions [1]_ :

  *(i) Influx of* :math:`Ca^{2+}` *due to Calcium currents*

  :math:`Ca^{2+}` ions enter through :math:`Ca^{2+}` channels and diffuse into the
  interior of the cell. Only the :math:`Ca^{2+}` concentration in a thin shell beneath
  the membrane was modeled. The influx of :math:`Ca^{2+}` into such a thin shell followed:

  .. math::

      [Ca]_{i}=-\frac{k}{2 F d} I_{Ca}

  where :math:`F=96489\, \mathrm{C\, mol^{-1}}` is the Faraday constant,
  :math:`d=1\, \mathrm{\mu m}` is the depth of the shell beneath the membrane,
  the unit conversion constant is :math:`k=0.1` for :math:`I_T` in
  :math:`\mathrm{\mu A/cm^{2}}` and :math:`[Ca]_{i}` in millimolar,
  and :math:`I_{Ca}` is the summation of all :math:`Ca^{2+}` currents.

  *(ii) Efflux of* :math:`Ca^{2+}` *due to an active pump*

  In a thin shell beneath the membrane, :math:`Ca^{2+}` retrieval usually consists of a
  combination of several processes, such as binding to :math:`Ca^{2+}` buffers, calcium
  efflux due to :math:`Ca^{2+}` ATPase pump activity and diffusion to neighboring shells.
  Only the :math:`Ca^{2+}` pump was modeled here. We adopted the following kinetic scheme:

  .. math::

      Ca _{i}^{2+}+ P \overset{c_1}{\underset{c_2}{\rightleftharpoons}} CaP \xrightarrow{c_3} P+ Ca _{0}^{2+}

  where P represents the :math:`Ca^{2+}` pump, CaP is an intermediate state,
  :math:`Ca _{ o }^{2+}` is the extracellular :math:`Ca^{2+}` concentration,
  and :math:`c_{1}, c_{2}` and :math:`c_{3}` are rate constants. :math:`Ca^{2+}`
  ions have a high affinity for the pump :math:`P`, whereas extrusion of
  :math:`Ca^{2+}` follows a slower process (Blaustein, 1988 ). Therefore,
  :math:`c_{3}` is low compared to :math:`c_{1}` and :math:`c_{2}` and the
  Michaelis-Menten approximation can be used for describing the kinetics of the pump.
  According to such a scheme, the kinetic equation for the :math:`Ca^{2+}` pump is:

  .. math::

      \frac{[Ca^{2+}]_{i}}{dt}=-\frac{K_{T}[Ca]_{i}}{[Ca]_{i}+K_{d}}

  where :math:`K_{T}=10^{-4}\, \mathrm{mM\, ms^{-1}}` is the product of :math:`c_{3}`
  with the total concentration of :math:`P` and :math:`K_{d}=c_{2} / c_{1}=10^{-4}\, \mathrm{mM}`
  is the dissociation constant, which can be interpreted here as the value of
  :math:`[Ca]_{i}` at which the pump is half activated (if :math:`[Ca]_{i} \ll K_{d}`
  then the efflux is negligible).

  **2.A simple first-order model**

  While, in (Bazhenov, et al., 1998) [2]_, the :math:`Ca^{2+}` dynamics is
  described by a simple first-order model,

  .. math::

      \frac{d\left[Ca^{2+}\right]_{i}}{d t}=-\frac{I_{Ca}}{z F d}+\frac{\left[Ca^{2+}\right]_{rest}-\left[C a^{2+}\right]_{i}}{\tau_{Ca}}

  where :math:`I_{Ca}` is the summation of all :math:`Ca ^{2+}` currents, :math:`d`
  is the thickness of the perimembrane "shell" in which calcium is able to affect
  membrane properties :math:`(1.\, \mathrm{\mu M})`, :math:`z=2` is the valence of the
  :math:`Ca ^{2+}` ion, :math:`F` is the Faraday constant, and :math:`\tau_{C a}` is
  the :math:`Ca ^{2+}` removal rate. The resting :math:`Ca ^{2+}` concentration was
  set to be :math:`\left[ Ca ^{2+}\right]_{\text {rest}}=.05\, \mathrm{\mu M}` .

  **3. The reversal potential**

  The reversal potential of calcium :math:`Ca ^{2+}` is calculated according to the
  Nernst equation:

  .. math::

      E = k'{RT \over 2F} log{[Ca^{2+}]_0 \over [Ca^{2+}]_i}

  where :math:`R=8.31441 \, \mathrm{J} /(\mathrm{mol}^{\circ} \mathrm{K})`,
  :math:`T=309.15^{\circ} \mathrm{K}`,
  :math:`F=96,489 \mathrm{C} / \mathrm{mol}`,
  and :math:`\left[\mathrm{Ca}^{2+}\right]_{0}=2 \mathrm{mM}`.

  Parameters
  ----------
  d : float
    The thickness of the perimembrane "shell".
  F : float
    The Faraday constant. (:math:`C*mmol^{-1}`)
  tau : float
    The time constant of the :math:`Ca ^{2+}` removal rate. (ms)
  C_rest : float
    The resting :math:`Ca ^{2+}` concentration.
  C_0 : float
    The :math:`Ca ^{2+}` concentration outside of the membrane.
  R : float
    The gas constant. (:math:` J*mol^{-1}*K^{-1}`)

  References
  ----------

  .. [1] Destexhe, Alain, Agnessa Babloyantz, and Terrence J. Sejnowski. "Ionic mechanisms for intrinsic slow oscillations in thalamic relay neurons." Biophysical journal 65, no. 4 (1993): 1538-1552.
  .. [2] Bazhenov, Maxim, Igor Timofeev, Mircea Steriade, and Terrence J. Sejnowski. "Cellular and network models for intrathalamic augmenting responses during 10-Hz stimulation." Journal of neurophysiology 79, no. 5 (1998): 2730-2748.

  """
  allowed_params = ('d', 'F', 'C_rest', 'tau', 'C_0', 'T', 'R')

  def __init__(self, size, method, d=1., F=96.489, C_rest=0.05, tau=5., C_0=2., T=36., R=8.31441, name=None):
    super(CaDyn, self).__init__(size, method, name=name)

    self.R = R  # gas constant, J*mol-1*K-1
    self.T = T
    self.d = d
    self.F = F
    self.tau = tau
    self.C_rest = C_rest
    self.C_0 = C_0

    # Concentration of the Calcium
    self.C = bm.Variable(bm.ones(self.num, dtype=bm.float_) * self.C_rest)
    # The dynamical reversal potential
    self.E = bm.Variable(bm.ones(self.num, dtype=bm.float_) * 120.)
    # Used to receive all Calcium currents
    self.I_Ca = bm.Variable(bm.zeros(self.num, dtype=bm.float_))

  def derivative(self, C, t, ICa):
    dCdt = - ICa / (2 * self.F * self.d) + (self.C_rest - C) / self.tau
    return dCdt

  def update(self, _t, _dt):
    self.C.value = self.integral(self.C.value, _t, self.I_Ca.value, dt=_dt)
    self.E.value = self.R * (273.15 + self.T) / (2 * self.F) * bm.log(self.C_0 / self.C.value)
    self.I_Ca[:] = 0.


class IAHP(CalChannel):
  r"""The calcium-dependent potassium current model.

  The dynamics of the calcium-dependent potassium current model is given by:

  .. math::

      \begin{aligned}
      I_{AHP} &= g_{\mathrm{max}} p (V - E) \\
      {dp \over dt} &= {p_{\infty}(V) - p \over \tau_p(V)} \\
      p_{\infty} &=\frac{48[Ca^{2+}]_i}{\left(48[Ca^{2+}]_i +0.09\right)} \\
      \tau_p &=\frac{1}{\left(48[Ca^{2+}]_i +0.09\right)}
      \end{aligned}

  where :math:`E` is the reversal potential, :math:`g_{max}` is the maximum conductance.


  Parameters
  ----------
  g_max : float
    The maximal conductance density (:math:`mS/cm^2`).
  E : float
    The reversal potential (mV).

  References
  ----------

  .. [1] Contreras, D., R. Curró Dossi, and M. Steriade. "Electrophysiological
         properties of cat reticular thalamic neurones in vivo." The Journal of
         Physiology 470.1 (1993): 273-294.
  .. [2] Mulle, Ch, Anamaria Madariaga, and M. Deschênes. "Morphology and
         electrophysiological properties of reticularis thalami neurons in
         cat: in vivo study of a thalamic pacemaker." Journal of
         Neuroscience 6.8 (1986): 2134-2145.
  .. [3] Avanzini, G., et al. "Intrinsic properties of nucleus reticularis
         thalami neurones of the rat studied in vitro." The Journal of
         Physiology 416.1 (1989): 111-122.
  .. [4] Destexhe, Alain, et al. "A model of spindle rhythmicity in the isolated
         thalamic reticular nucleus." Journal of neurophysiology 72.2 (1994): 803-818.
  .. [5] Vijayan S, Kopell NJ (2012) Thalamic model of awake alpha oscillations and
         implications for stimulus processing. Proc Natl Acad Sci USA 109: 18553–18558.

  """

  allowed_params = ('E', 'g_max')

  def __init__(self, ca, size, method='exponential_euler', E=-80., g_max=1., name=None):
    super(IAHP, self).__init__(size, method, name=name)

    # parameters
    self.E = E
    self.g_max = g_max
    self.ca = ca
    assert isinstance(ca, CaDyn)

    # variables
    self.p = bm.Variable(bm.zeros(self.num, dtype=bm.float_))

  def derivative(self, p, t, C):
    C2 = 48 * C ** 2
    phi_p = C2 / (C2 + 0.09)
    p_inf = 1 / (C2 + 0.09)
    dpdt = (phi_p - p) / p_inf
    return dpdt

  def update(self, _t, _dt):
    self.p.value = self.integral(self.p.value, _t, C=self.ca.C.value, dt=_dt)

  def current(self, V):
    g = self.g_max * self.p.value
    return g * (self.E - V)


class ICaN(CalChannel):
  r"""The calcium-activated non-selective cation channel model.

  The dynamics of the calcium-activated non-selective cation channel model is given by:

  .. math::

      \begin{aligned}
      I_{CAN} &=g_{\mathrm{max}} M\left([Ca^{2+}]_{i}\right) p \left(V-E\right)\\
      &M\left([Ca^{2+}]_{i}\right) ={[Ca^{2+}]_{i} \over 0.2+[Ca^{2+}]_{i}} \\
      &{dp \over dt} = {\phi \cdot (p_{\infty}-p)\over \tau_p} \\
      &p_{\infty} = {1.0 \over 1 + \exp(-(V + 43) / 5.2)} \\
      &\tau_{p} = {2.7 \over \exp(-(V + 55) / 15) + \exp((V + 55) / 15)} + 1.6
      \end{aligned}

  where :math:`\phi` is the temperature factor.

  Parameters
  ----------
  g_max : float
    The maximal conductance density (:math:`mS/cm^2`).
  E : float
    The reversal potential (mV).
  phi : float
    The temperature factor.

  References
  ----------

  .. [1] Destexhe, Alain, et al. "A model of spindle rhythmicity in the isolated
         thalamic reticular nucleus." Journal of neurophysiology 72.2 (1994): 803-818.
  .. [2] Inoue T, Strowbridge BW (2008) Transient activity induces a long-lasting
         increase in the excitability of olfactory bulb interneurons.
         J Neurophysiol 99: 187–199.
  """
  allowed_params = ('E', 'g_max', 'phi')

  def __init__(self, host, method, E=10., g_max=1., phi=1., name=None):
    super(ICaN, self).__init__(host, method, name=name)

    self.E = E
    self.g_max = g_max
    self.phi = phi

    assert hasattr(self.host, 'ca') and isinstance(self.host.ca, CaDyn)
    self.p = bm.Variable(bm.zeros(self.host.num, dtype=bm.float_))

  def derivative(self, p, t, V):
    phi_p = 1.0 / (1 + bm.exp(-(V + 43.) / 5.2))
    p_inf = 2.7 / (bm.exp(-(V + 55.) / 15.) + bm.exp((V + 55.) / 15.)) + 1.6
    dpdt = self.phi * (phi_p - p) / p_inf
    return dpdt

  def update(self, _t, _dt):
    self.p.value = self.integral(self.p.value, _t, self.host.V.value, dt=_dt)

  def current(self):
    M = self.host.ca.C.value / (self.host.ca.C.value + 0.2)
    g = self.g_max * M * self.p.value
    return g * (self.E - self.host.V.value)


class ICaT(CalChannel):
  r"""The low-threshold T-type calcium current model.

  The dynamics of the low-threshold T-type calcium current model [1]_ is given by:

  .. math::

      I_{CaT} &= g_{max} p^2 q(V-E_{Ca}) \\
      {dp \over dt} &= {\phi_p \cdot (p_{\infty}-p)\over \tau_p} \\
      &p_{\infty} = {1 \over 1+\exp [-(V+59-V_{sh}) / 6.2]} \\
      &\tau_{p} = 0.612 + {1 \over \exp [-(V+132.-V_{sh}) / 16.7]+\exp [(V+16.8-V_{sh}) / 18.2]} \\
      {dq \over dt} &= {\phi_q \cdot (q_{\infty}-q) \over \tau_q} \\
      &q_{\infty} = {1 \over 1+\exp [(V+83-V_{sh}) / 4]} \\
      & \begin{array}{l} \tau_{q} = \exp \left(\frac{V+467-V_{sh}}{66.6}\right)  \quad V< (-80 +V_{sh})\, mV  \\
          \tau_{q} = \exp \left(\frac{V+22-V_{sh}}{-10.5}\right)+28 \quad V \geq (-80 + V_{sh})\, mV \end{array}

  where :math:`phi_p = 3.55^{\frac{T-24}{10}}` and :math:`phi_q = 3^{\frac{T-24}{10}}`
  are temperature-dependent factors (:math:`T` is the temperature in Celsius),
  :math:`E_{Ca}` is the reversal potential of Calcium channel.

  Parameters
  ----------
  T : float
    The temperature.
  T_base_p : float
    The base temperature factor of :math:`p` channel.
  T_base_q : float
    The base temperature factor of :math:`q` channel.
  g_max : float
    The maximum conductance.
  V_sh : float
    The membrane potential shift.

  References
  ----------

  .. [1] Huguenard JR, McCormick DA (1992) Simulation of the currents involved in
         rhythmic oscillations in thalamic relay neurons. J Neurophysiol 68:1373–1383.

  """

  def __init__(self, host, method, T=36., T_base_p=3.55, T_base_q=3., g_max=2., V_sh=-3., name=None):
    super(ICaT, self).__init__(host, method, name=name)
    self.T = T
    self.T_base_p = T_base_p
    self.T_base_q = T_base_q
    self.g_max = g_max
    self.V_sh = V_sh

    assert hasattr(self.host, 'ca') and isinstance(self.host.ca, Ca)
    self.p = bm.Variable(bm.zeros(host.num, dtype=bm.float_))
    self.q = bm.Variable(bm.zeros(host.num, dtype=bm.float_))

  def derivative(self, p, q, t, V):
    phi_p = self.T_base_p ** ((self.T - 24) / 10)
    p_inf = 1. / (1 + bm.exp(-(V + 59. - self.V_sh) / 6.2))
    p_tau = 1. / (bm.exp(-(V + 132. - self.V_sh) / 16.7) + bm.exp((V + 16.8 - self.V_sh) / 18.2)) + 0.612
    dpdt = phi_p * (p_inf - p) / p_tau

    phi_q = self.T_base_q ** ((self.T - 24) / 10)
    q_inf = 1. / (1. + bm.exp((V + 83. - self.V_sh) / 4.0))
    q_tau = bm.where(V >= (-80. + self.V_sh),
                     bm.exp(-(V + 22. - self.V_sh) / 10.5) + 28.,
                     bm.exp((V + 467. - self.V_sh) / 66.6))
    dqdt = phi_q * (q_inf - q) / q_tau

    return dpdt, dqdt

  def update(self, _t, _dt):
    p, q = self.integral(self.p.value, self.q.value, _t, self.host.V.value, dt=_dt)
    self.p.value, self.q.value = p, q

  def current(self):
    g = self.g_max * self.p.value ** 2 * self.q.value
    return g * (self.host.ca.E - self.host.V.value)


class ICaT_RE(CalChannel):
  r"""The low-threshold T-type calcium current model in thalamic reticular nucleus.

  The dynamics of the low-threshold T-type calcium current model [1]_ [2]_ in thalamic
  reticular nucleus neurons is given by:

  .. math::

      I_{CaT} &= g_{max} p^2 q(V-E_{Ca}) \\
      {dp \over dt} &= {\phi_p \cdot (p_{\infty}-p)\over \tau_p} \\
      &p_{\infty} = {1 \over 1+\exp [-(V+52-V_{sh}) / 7.4]}  \\
      &\tau_{p} = 3+{1 \over \exp [(V+27-V_{sh}) / 10]+\exp [-(V+102-V_{sh}) / 15]} \\
      {dq \over dt} &= {\phi_q \cdot (q_{\infty}-q) \over \tau_q} \\
      &q_{\infty} = {1 \over 1+\exp [(V+80-V_{sh}) / 5]} \\
      & \tau_q = 85+ {1 \over \exp [(V+48-V_{sh}) / 4]+\exp [-(V+407-V_{sh}) / 50]}

  where :math:`phi_p = 5^{\frac{T-24}{10}}` and :math:`phi_q = 3^{\frac{T-24}{10}}`
  are temperature-dependent factors (:math:`T` is the temperature in Celsius),
  :math:`E_{Ca}` is the reversal potential of Calcium channel.

  Parameters
  ----------
  T : float
    The temperature.
  T_base_p : float
    The base temperature factor of :math:`p` channel.
  T_base_q : float
    The base temperature factor of :math:`q` channel.
  g_max : float
    The maximum conductance.
  V_sh : float
    The membrane potential shift.

  References
  ----------

  .. [1] Avanzini, G., et al. "Intrinsic properties of nucleus reticularis thalami
         neurones of the rat studied in vitro." The Journal of
         Physiology 416.1 (1989): 111-122.
  .. [2] Bal, Thierry, and DAVID A. McCORMICK. "Mechanisms of oscillatory activity
         in guinea‐pig nucleus reticularis thalami in vitro: a mammalian
         pacemaker." The Journal of Physiology 468.1 (1993): 669-691.

  """

  def __init__(self, host, method, T=36., T_base_p=5., T_base_q=3.,
               g_max=1.75, V_sh=-3., name=None):
    super(ICaT_RE, self).__init__(host, method, name=name)
    self.T = T
    self.T_base_p = T_base_p
    self.T_base_q = T_base_q
    self.g_max = g_max
    self.V_sh = V_sh

    self.p = bm.Variable(bm.zeros(host.num, dtype=bm.float_))
    self.q = bm.Variable(bm.zeros(host.num, dtype=bm.float_))

  def dp(self, p, t, V):
    phi_p = self.T_base_p ** ((self.T - 24) / 10)
    p_inf = 1. / (1. + bm.exp(-(V + 52. - self.V_sh) / 7.4))
    p_tau = 3. + 1. / (bm.exp((V + 27. - self.V_sh) / 10.) + bm.exp(-(V + 102. - self.V_sh) / 15.))
    dpdt = phi_p * (p_inf - p) / p_tau
    return dpdt

  def dq(self, q, t, V):
    phi_q = self.T_base_q ** ((self.T - 24) / 10)
    q_inf = 1. / (1. + bm.exp((V + 80. - self.V_sh) / 5.))
    q_tau = 85. + 1. / (bm.exp((V + 48. - self.V_sh) / 4.) + bm.exp(-(V + 407. - self.V_sh) / 50.))
    dqdt = phi_q * (q_inf - q) / q_tau
    return dqdt

  def derivative(self, p, q, t, V):
    return bp.Join

  def current(self, V):
    g = self.g_max * self.p.value ** 2 * self.q.value
    return g * (self.host.ca.E - V)


class ICaHT(CalChannel):
  r"""The high-threshold T-type calcium current model.

  The high-threshold T-type calcium current model is adopted from [1]_.
  Its dynamics is given by

  .. math::

      \begin{aligned}
      I_{\mathrm{Ca/HT}} &= g_{\mathrm{max}} p^2 q (V-E_{Ca})
      \\
      {dp \over dt} &= {\phi_{p} \cdot (p_{\infty} - p) \over \tau_{p}} \\
      &\tau_{p} =\frac{1}{\exp \left(\frac{V+132-V_{sh}}{-16.7}\right)+\exp \left(\frac{V+16.8-V_{sh}}{18.2}\right)}+0.612 \\
      & p_{\infty} = {1 \over 1+exp[-(V+59-V_{sh}) / 6.2]}
      \\
      {dq \over dt} &= {\phi_{q} \cdot (q_{\infty} - h) \over \tau_{q}} \\
      & \begin{array}{l} \tau_q = \exp \left(\frac{V+467-V_{sh}}{66.6}\right)  \quad V< (-80 +V_{sh})\, mV  \\
      \tau_q = \exp \left(\frac{V+22-V_{sh}}{-10.5}\right)+28 \quad V \geq (-80 + V_{sh})\, mV \end{array} \\
      &q_{\infty}  = {1 \over 1+exp[(V+83 -V_{shift})/4]}
      \end{aligned}

  where :math:`phi_p = 3.55^{\frac{T-24}{10}}` and :math:`phi_q = 3^{\frac{T-24}{10}}`
  are temperature-dependent factors (:math:`T` is the temperature in Celsius),
  :math:`E_{Ca}` is the reversal potential of Calcium channel.

  Parameters
  ----------
  T : float
    The temperature.
  T_base_p : float
    The base temperature factor of :math:`p` channel.
  T_base_q : float
    The base temperature factor of :math:`q` channel.
  g_max : float
    The maximum conductance.
  V_sh : float
    The membrane potential shift.

  References
  ----------
  .. [1] Huguenard JR, McCormick DA (1992) Simulation of the currents involved in
         rhythmic oscillations in thalamic relay neurons. J Neurophysiol 68:1373–1383.
  """

  def __init__(self, host, method, T=36., T_base_p=3.55,
               T_base_q=3., g_max=2., V_sh=25., name=None):
    super(ICaHT, self).__init__(host, method, name=name)

    self.T = T
    self.T_base_p = T_base_p
    self.T_base_q = T_base_q
    self.g_max = g_max
    self.V_sh = V_sh

    assert hasattr(self.host, 'ca') and isinstance(self.host.ca, Ca)
    self.p = bm.Variable(bm.zeros(host.num, dtype=bm.float_))
    self.q = bm.Variable(bm.zeros(host.num, dtype=bm.float_))

  def derivative(self, p, q, t, V):
    phi_p = self.T_base_p ** ((self.T - 24) / 10)
    p_inf = 1. / (1. + bm.exp(-(V + 59. - self.V_sh) / 6.2))
    p_tau = 1. / (bm.exp(-(V + 132. - self.V_sh) / 16.7) + bm.exp((V + 16.8 - self.V_sh) / 18.2)) + 0.612
    dpdt = phi_p * (p_inf - p) / p_tau

    phi_q = self.T_base_q ** ((self.T - 24) / 10)
    q_inf = 1. / (1. + bm.exp((V + 83. - self.V_sh) / 4.))
    q_tau = bm.where(V >= (-80. + self.V_sh),
                     bm.exp(-(V + 22. - self.V_sh) / 10.5) + 28.,
                     bm.exp((V + 467. - self.V_sh) / 66.6))
    dqdt = phi_q * (q_inf - q) / q_tau

    return dpdt, dqdt

  def current(self, V, p, q):
    g = self.g_max * p * p * q
    return g * (self.host.ca.E - V)


class ICaL(CalChannel):
  r"""The L-type calcium channel model.

  The L-type calcium channel model is adopted from (Inoue, et, al., 2008) [1]_.
  Its dynamics is given by:

  .. math::

      I_{CaL} &= g_{max} p^2 q(V-E_{Ca}) \\
      {dp \over dt} &= {\phi_p \cdot (p_{\infty}-p)\over \tau_p} \\
      &p_{\infty} = {1 \over 1+\exp [-(V+10-V_{sh}) / 4.]} \\
      &\tau_{p} = 0.4+{0.7 \over \exp [(V+5-V_{sh}) / 15]+\exp [-(V+5-V_{sh}) / 15]} \\
      {dq \over dt} &= {\phi_q \cdot (q_{\infty}-q) \over \tau_q} \\
      &q_{\infty} = {1 \over 1+\exp [(V+25-V_{sh}) / 2]} \\
      &\tau_q = 300 + {100 \over \exp [(V+40-V_{sh}) / 9.5]+\exp [-(V+40-V_{sh}) / 9.5]}

  where :math:`phi_p = 3.55^{\frac{T-24}{10}}` and :math:`phi_q = 3^{\frac{T-24}{10}}`
  are temperature-dependent factors (:math:`T` is the temperature in Celsius),
  :math:`E_{Ca}` is the reversal potential of Calcium channel.

  Parameters
  ----------
  T : float
    The temperature.
  T_base_p : float
    The base temperature factor of :math:`p` channel.
  T_base_q : float
    The base temperature factor of :math:`q` channel.
  g_max : float
    The maximum conductance.
  V_sh : float
    The membrane potential shift.

  References
  ----------

  .. [1] Inoue, Tsuyoshi, and Ben W. Strowbridge. "Transient activity induces a long-lasting
         increase in the excitability of olfactory bulb interneurons." Journal of
         neurophysiology 99, no. 1 (2008): 187-199.
  """

  def __init__(self, num, T=36., T_base_p=3.55, T_base_q=3., g_max=1., V_sh=0.):
    super(ICaL, self).__init__()

    # parameters
    self.T = T
    self.T_base_p = T_base_p
    self.T_base_q = T_base_q
    self.g_max = g_max
    self.V_sh = V_sh

    # variables
    self.p = bm.Variable(bm.zeros(num, dtype=bm.float_))
    self.q = bm.Variable(bm.zeros(num, dtype=bm.float_))

  def dp(self, p, t, V):
    phi_p = self.T_base_p ** ((self.T - 24) / 10)
    p_inf = 1. / (1 + bm.exp(-(V + 10. - self.V_sh) / 4.))
    p_tau = 0.4 + .7 / (bm.exp(-(V + 5. - self.V_sh) / 15.) + bm.exp((V + 5. - self.V_sh) / 15.))
    dpdt = phi_p * (p_inf - p) / p_tau
    return dpdt

  def dq(self, q, t, V):
    phi_q = self.T_base_q ** ((self.T - 24) / 10)
    q_inf = 1. / (1. + bm.exp((V + 25. - self.V_sh) / 2.))
    q_tau = 300. + 100. / (bm.exp((V + 40 - self.V_sh) / 9.5) + bm.exp(-(V + 40 - self.V_sh) / 9.5))
    dqdt = phi_q * (q_inf - q) / q_tau
    return dqdt

  @property
  def derivative(self):
    return bp.JointEq([self.dp, self.dq])

  def current(self, V, p, q):
    return self.g_max * p * p * q * (self.host.ca.E - V)
