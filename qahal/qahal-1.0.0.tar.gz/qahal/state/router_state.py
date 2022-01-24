from . import State

class RouterState(State):
  KWARGS = ('checks', 'states', 'else_')

  def __init__(self, checks, states, else_=None, **kwargs):
    super().__init__(**kwargs)
    
    self.checks = checks
    self.states = states
    self.else_ = else_
  
  def initialize(self):
    for check, state in zip(self.checks, self.states):
      if check(self.statelist):
        self.statelist.replace(state)
        break
    else:
      if self.else_ is not None:
        self.statelist.replace(self.else_)
      else:
        raise RuntimeError('no check passed')

