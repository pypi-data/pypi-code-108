from enum import Enum
import numpy as np

class DataTypes(Enum):
  video = 0
  audio  = 1
  feature = 2

'''Helper'''
def string_to_enum(enum, string):
  for e in enum:
    if e.scheme == string:
      return e
  raise ValueError('{} not part of enumeration  {}'.format(string, enum))
