# -*- coding: utf-8 -*-

from .base import IonChannel

__all__ = [
  'IL',
  'IKL',
]


class IL(IonChannel):
  """The leakage channel current.

  Parameters
  ----------
  g_max : float
    The leakage conductance.
  E : float
    The reversal potential.
  """
  allowed_params = ('E', 'g_max')

  def __init__(self, host, method, g_max=0.1, E=-70., name=None):
    super(IL, self).__init__(host, method, name=name)

    self.E = E
    self.g_max = g_max

  def update(self, _t, _dt):
    pass

  def current(self):
    return self.g_max * (self.E - self.host.V.value)


class IKL(IL):
  """The potassium leak channel current.

  Parameters
  ----------
  g_max : float
    The potassium leakage conductance which is modulated by both
    acetylcholine and norepinephrine.
  E : float
    The reversal potential.
  """

  def __init__(self, g_max=0.005, E=-90., name=None):
    super(IKL, self).__init__(g_max=g_max, E=E, name=name)


class Potential(IonChannel):
  pass


