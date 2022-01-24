from . import State
from ..utils import raiser

class CheckState(State):
  KWARGS = ('checks', 'cbs', 'else_')

  def __init__(self, checks, cbs,
      else_=lambda _: raiser(NotImplementedError), **kwargs):
    super().__init__(**kwargs)
    
    self.checks = checks
    self.cbs = cbs
    self.else_ = else_
  
  def initialize(self):
    for check, cb in zip(self.checks, self.cbs):
      if check(self.statelist):
        cb(self.statelist)
        break
    else:
      self.else_(self.statelist)

