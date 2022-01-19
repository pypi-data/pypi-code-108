#!/usr/bin/env python3
"""
# Created: Sun Jan  9 14:08:55 2022 (-0500)
# @author: jacobfaibussowitsch
"""
from ._warpobject import WarpObjectBase
from ._load       import LoadingBase
from ._load       import NodalLoad
from ._load       import StepLoad
from ._load       import Constraint
from ._list       import GeometricList
from ._util       import resolve_path

class Structure(WarpObjectBase):
  _typename = 'structure'

  def __init__(self,model,name):
    __doc__="""
    Create the structure

    Parameters
    ----------
    name : name of the structure, convertable to string
    """
    super().__init__(name)
    self._model   = model
    self._lines   = []
    self._objects = {
      "constraints" : [],
      "loads"       : [],
      "lists"       : []
    }
    self._model._add_object(self)
    return

  def _finalize(self):
    return '\n'+'\n'.join(map(str,self._lines))

  def _add_object(self,obj):
    if isinstance(obj,LoadingBase):
      object_name = "loads"
    elif isinstance(obj,Constraint):
      object_name = "constraints"
    elif isinstance(obj,GeometricList):
      object_name = "lists"
    else:
      raise TypeError(type(obj))
    self._objects[object_name].append(obj)
    self._lines.append(obj)
    return

  def input_from(self,*args,**kwargs):
    self._lines.append(self._model._input_from(*args,**kwargs))

  def compute(self,begin,end,load):
    assert load in self._objects["loads"]
    self._model._lines.append(f'compute displacements load {load._name} step {begin}-{end}')
    return

  def output(self,*args):
    self._model._lines.append(f'output flat text {" ".join(args)}')
    return
