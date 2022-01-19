#!/usr/bin/env python3
"""
# Created: Fri Jan 14 14:27:05 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import sys
import collections
from ._warpobject import WarpObjectBase
from ._util       import to_arglist

class ParameterBase(WarpObjectBase):
  def __init__(self,model,items):
    if not isinstance(items,collections.OrderedDict):
      raise TypeError(type(items))

    super().__init__()

    self._items = collections.OrderedDict()
    if sys.version_info >= (3,6):
      # orderd dict comprehensions by default since python 3.6
      self.set_parameters(**items)
    else:
      for key,value in items.items():
        self._items[key.replace("_"," ")] = value
    model._add_object(self)
    return

  def _finalize(self):
    def truthy(sep,key,val):
      return sep.join((key,'on'))

    def falsey(sep,key,val):
      return sep.join((key,'off'))

    return to_arglist(self._items,truthy=truthy,falsey=falsey)

  def set_parameters(self,**kwargs):
    kwargs = {k.replace("_"," ") : v for k,v in kwargs.items()}
    self._items.update(**kwargs)

class SolutionParameters(ParameterBase):
  _typename = "solution parameters"

  def __init__(self,*args,**kwargs):
    items = collections.OrderedDict(
      solution_technique=kwargs.pop("solution_technique","sparse direct"),**kwargs
    )
    super().__init__(*args,items)
    return


class CrackGrowthParameters(ParameterBase):
  _typename = "crack growth parameters"

  def __init__(self,*args,**kwargs):
    items = collections.OrderedDict(
      type_of_crack_growth=kwargs.pop("type_of_crack_growth","cohesive"),**kwargs
    )
    super().__init__(*args,items)
    return
