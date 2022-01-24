from . import State

class InputState(State):
  KWARGS = ('message', 'converter')

  def __init__(self, message='', converter=None, **kwargs):
    super().__init__(**kwargs)
    
    self.message = message
    
    if converter is not None:
      self.converter = converter
    else:
      self.converter = self.default_converter
  
  def initialize(self):
    print(self.message, end='', flush=True)
  
  @staticmethod
  def default_converter(value):
      return value
  
  def handle(self, value):
      value = self.converter(value)
      self.statelist.state[-2].handle(value)

