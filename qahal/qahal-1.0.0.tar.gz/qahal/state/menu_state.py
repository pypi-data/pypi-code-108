from . import State

class MenuState(State):
  ARGS = 'items'

  def __init__(self, *items, **kwargs):
    super().__init__(**kwargs)
    
    self.items = items
  
  def initialize(self):
    self.show_items()
  
  def show_items(self):
    for idx, c in enumerate(self.items):
      print(f'{idx}- {c["name"]}')
    
    if self.can_back:
      print('b- back')
  
  def handle(self, value):
    try:
      if self.can_back and value == 'b':
        self.statelist.prev()
      else:
        self.statelist.move(self.items[int(value)]['state'])
    except (ValueError, IndexError) as e:
      self.on_error(value, e)
  
  def on_error(self, value, e):
    print('choose a value from menu')
    self.statelist.run()
  
  @property
  def can_back(self):
    return len(self.statelist.state) > 1

