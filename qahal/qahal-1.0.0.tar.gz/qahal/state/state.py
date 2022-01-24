class State:
  ARGS = None
  KWARGS = []
  
  def __init__(self, *, name=''):
    self.name = name
    self.attrs = {}
  
  def __call__(self):
    args = getattr(self, self.ARGS) if self.ARGS is not None else []
    kwargs = {c: getattr(self, c) for c in self.KWARGS}
    
    return type(self)(*args, **kwargs, name=self.name)
  
  def handle(self, value):
    raise NotImplementedError
  
  def initialize(self):
    pass
  
  def set_attrs(self, **attrs):
    for c in attrs:
      self.attrs[c] = attrs[c]
  
  def to_dict(self, value=None, cls=None):
    return {'attrs': self.attrs, '__state_name__': self.name}
  
  @staticmethod
  def from_dict(value, states):
    names = [s.name for s in states]
    
    if '__state_name__' not in value:
      return value
    else:
      state_name = value['__state_name__']
      state = states[names.index(state_name)]
      obj = state()
      obj.set_attrs(**value['attrs'])
      return obj

