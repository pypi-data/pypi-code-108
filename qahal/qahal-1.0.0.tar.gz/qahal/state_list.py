import json
from functools import partial
from .state import State

def run_after(f):
  def call(self, *args, **kwargs):
    f(self, *args, **kwargs)
    self.run()
  
  return call

class StateList:
  def __init__(self, state=None, **attrs):
    if state is None:
      self.state = []
    else:
      self.state = list(state)
    
    self.attrs = dict(attrs)
  
  @run_after
  def move(self, state):
    self.state.append(state())
  
  @run_after
  def prev(self, count=1):
    for c in range(count):
      self.state.pop()
  
  @run_after
  def replace(self, state):
    self.state[-1] = state()
  
  @run_after
  def set(self, *state):
    self.state.clear()
    self.state.extend(state)
  
  def run(self):
    self.state[-1].statelist = self
    self.state[-1].initialize()
  
  def handle(self, value):
    self.state[-1].handle(value)
  
  def loop(self, input_func=input):
    while True:
      try:
        self.handle(input_func())
      except EOFError:
        break
  
  def to_dict(self):
    return {
      'attrs': self.attrs,
      'state': [c.to_dict() for c in self.state],
      '__state_name__': 'state_list'
    }
  
  @classmethod
  def from_dict(cls, value, states):
    if '__state_name__' not in value:
      return value
    elif value['__state_name__'] == 'state_list':
      return cls(state=value['state'], **value['attrs'])
    else:
      return State.from_dict(value, states)
  
  def json_dump(self):
    return json.dumps(self.to_dict())
  
  @classmethod
  def json_load(cls, value, states):
    return json.loads(value, object_hook=partial(cls.from_dict, states=states))

