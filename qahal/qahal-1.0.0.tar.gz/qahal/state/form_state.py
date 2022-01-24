from . import State

class FormState(State):
  ARGS = 'inputs'
  KWARGS = ['on_submit']
  
  def __init__(self, *inputs, on_submit=lambda f, sl: None, **kwargs):
    super().__init__(**kwargs)
    
    self.inputs = inputs
    self.on_submit = on_submit
    self.attrs['idx'] = 0
  
  def prev(self):
    self.attrs['idx'] -= 1
    self.statelist.prev()
  
  def initialize(self):
    if 0 <= self.attrs['idx'] < len(self.inputs):
      state = self.inputs[self.attrs['idx']]['state']
      self.statelist.move(state())
    elif self.attrs['idx'] < 0:
      self.statelist.prev()
    else:
      self.submit()
      self.statelist.prev()
  
  def handle(self, value):
    name = self.inputs[self.attrs['idx']]['name']
    self.attrs[name] = value
    self.attrs['idx'] += 1
    self.statelist.prev()
  
  def submit(self):
    values = {}
    for c in self.inputs:
      values[c['name']] = self.attrs[c['name']]
    
    self.on_submit(self.statelist, values)

