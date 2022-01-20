from html import escape
from jcramda import when
from jcramda.base.comparison import is_a_tuple, is_a_str


def _escape(raw):
  if raw.startswith('{{') and raw.endswith('}}'):
    return raw.strip('{{').strip('}}')
  if is_a_str(raw):
    return f"'{escape(raw)}'"
  return str(raw)


_value_check = when(
  (is_a_str, lambda s: f' = {_escape(s)}'),
  (is_a_tuple, lambda tp: f'{tp[0]} {_escape(tp[1])}'),
  else_=str
)


class where:
  def __init__(self, raw):
      self.raw = raw
  
  def __str__(self):
    tn = getattr(type(self.raw), '__name__')
    method = getattr(self, f'from_{tn}')
    if callable(method):
      return method()
    else:
      return str(self.raw)
  
  def from_dict(self):
    """
    Example:
    >>> w = where({'name': 'someone', 'age': ('>', 32), 'birthday': '{{CURRENT_DATE}}'})
    >> print(w)
       name = 'someone' AND 'age' > 32 AND birthday = CURRENT_DATE
    """
    return ' AND '.join([f'{key} {_value_check(value)}' for key, value in self.raw.items()])

