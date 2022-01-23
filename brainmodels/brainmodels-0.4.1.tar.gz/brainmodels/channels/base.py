# -*- coding: utf-8 -*-

import brainpy as bp
import brainpy.math as bm
from brainpy import errors
from brainpy.base import Collector
from brainpy.building import brainobjects

from brainmodels.neurons.base import Neuron

__all__ = [
  'Channel',
  'MolChannel',
  'IonChannel',
  'CalChannel',

  'CondNeuGroup',
]


class Channel(brainobjects.Channel):
  """Base class to model ion channels.

  Notes
  -----

  The ``__init__()`` function in :py:class:`Channel` is used to specify
  the parameters of the channel. The ``__call__()`` function
  is used to initialize the variables in this channel.
  """
  allowed_params = None

  def __init__(self, size, method, name=None):
    super(Channel, self).__init__(name=name)

    self.size = size
    self.method = method
    self.num = bp.tools.size2num(size)

    self.integral = bp.odeint(self.derivative, method=method)

  def update(self, _t, _dt):
    """The function to specify the updating rule."""
    raise NotImplementedError(f'Subclass must implement "update" function.')

  def derivative(self, *args, **kwargs):
    raise NotImplementedError

  @classmethod
  def make(cls, **params):
    """Set the default parameters for later class initialization.
    Return a tuple of `(cls, params)`. """
    if cls.allowed_params is None:
      return cls, params
    else:
      assert isinstance(cls.allowed_params, (tuple, list))
      allowed_params = tuple(cls.allowed_params)
      for p in params:
        assert p in allowed_params, f'{p} is not allowed to define in {cls}. ' \
                                    f'The allowed params include: {allowed_params}'
      return cls, params


class MolChannel(Channel):
  pass


class IonChannel(Channel):
  def current(self, *args, **kwargs):
    raise NotImplementedError


class CalChannel(IonChannel):
  pass


class Cluster(bp.DynamicalSystem):
  pass


class CondNeuGroup(Neuron):
  """Base class to model conductance-based neuron group.

  The standard formulation for a conductance-based model is given as

  .. math::

      C_m {dV \over dt} = \sum_jg_j(E - V) + I_{ext}

  where :math:`g_j=\bar{g}_{j} M^x N^y` is the channel conductance, :math:`E` is the
  reversal potential, :math:`M` is the activation variable, and :math:`N` is the
  inactivation variable.

  :math:`M` and :math:`N` have the dynamics of

  .. math::

      {dx \over dt} = \phi_x {x_\infty (V) - x \over \tau_x(V)}

  where :math:`x \in [M, N]`, :math:`\phi_x` is a temperature-dependent factor,
  :math:`x_\infty` is the steady state, and :math:`\tau_x` is the time constant.
  Equivalently, the above equation can be written as:

  .. math::

      \frac{d x}{d t}=\phi_{x}\left(\alpha_{x}(1-x)-\beta_{x} x\right)

  where :math:`\alpha_{x}` and :math:`\beta_{x}` are rate constants.

  Parameters
  ----------
  size : int, tuple of int
    The network size of this neuron group.
  num_batch : optional, int
    The batch size.
  name : optional, str
    The neuron group name.

  Notes
  -----

  The ``__init__()`` function in :py:class:`CondNeuGroup` is used to specify
  the parameters of channels and this neuron group. The ``__call__()`` function
  is used to initialize the variables in this neuron group.
  """
  def __init__(self, size, C=1., A=1e-3, V_th=0., method='exp_auto', name=None, **channels):
    super(CondNeuGroup, self).__init__(size, method=method, name=name)

    # parameters for neurons
    self.C = C
    self.A = A
    self.V_th = V_th

    # check 'channels'
    _channels = dict()
    for key in channels.items():
      assert isinstance(key, str), f'Key must be a str, but got {type(key)}: {key}'
      assert isinstance(channels[key], (tuple, list)) and len(channels[key]) == 2
      assert isinstance(channels[key][0], type)
      assert isinstance(channels[key][1], dict)
      cls = channels[key][0]
      params = channels[key][1].copy()
      params['host'] = self
      params['method'] = method
      _channels[key] = (cls, params)

    # initialize children channels
    self.channels = Collector()
    for key, (ch, params) in _channels.items():
      self.channels[key] = ch(**params)
      if not isinstance(self.channels[key], Channel):
        raise errors.BrainPyError(f'{self.__class__.__name__} only receives {Channel} instance, '
                                  f'while we got {type(self.channels[key])}: {self.channels[key]}.')

    self.ion_channels = self.channels.subset(IonChannel)
    self.mol_channels = self.channels.subset(MolChannel)

  def derivative(self, V, t, Iext):
    self.V.value = V
    Iext *= (1e-3 / self.A)
    for ch in self.ion_channels.values():
      Iext += ch.current()
    return Iext / self.C

  def update(self, _t, _dt):
    # update variables in channels
    for ch in self.ion_channels.values():
      ch.update(_t, _dt)

    # update neuron variables
    V = self.integral(self.V.value, _t, self.input.value, dt=_dt)
    self.spike[:] = bm.logical_and(V >= self.V_th, self.V < self.V_th)
    self.input[:] = 0.
    self.V[:] = V

  def __getattr__(self, item):
    """Wrap the dot access ('self.'). """
    channels = super(CondNeuGroup, self).__getattribute__('channels')
    if item in channels:
      return channels[item]
    else:
      return super(CondNeuGroup, self).__getattribute__(item)

  @classmethod
  def make(cls, C=1., A=1e-3, V_th=0., **channels):
    for name, ch in channels.items():
      assert len(ch) == 2
      assert isinstance(ch[0], type)
      assert isinstance(ch[1], dict)

    def generate_cond_neuron_group(size, method='exp_auto', name=None):
      return cls(
        C=C, A=A, V_th=V_th,  # membrane potential parameters
        size=size, method=method, name=name,  # initialization parameters
        **channels  # channel settings
      )

    return generate_cond_neuron_group
