#from __future__ import annotations

from lb_pidsim_train.callbacks.schedulers import GanBaseLrScheduler

class GanExpLrScheduler (GanBaseLrScheduler):   # TODO add docstring
  """class description"""
  def __init__ (self, factor = 0.1, step = 1):   # TODO add data-type check
    super().__init__()
    self._factor = factor
    self._step = step

  def _scheduled_lr (self, lr0, epoch):
    return lr0 * self._factor ** (epoch / self._step)
