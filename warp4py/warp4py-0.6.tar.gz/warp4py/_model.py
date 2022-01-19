#!/usr/bin/env python3
"""
# Created: Sun Jan  9 14:29:53 2022 (-0500)
# @author: jacobfaibussowitsch
"""
from ._warpobject import WarpObjectBase
from ._util       import resolve_path
from ._structure  import Structure
from ._material   import Material
from ._load       import StepLoad
from ._load       import NodalLoad

class Model(WarpObjectBase):
  def __init__(self,name):
    __doc__="""

    Parameters
    ----------
    name : name of the model
    """
    super().__init__(name)
    self._lines   = []
    self._objects = []
    return

  def _add_object(self,obj):
    self._lines.append(obj)
    self._objects.append(obj)
    return

  def view(self):
    print(
      '! '+self._name,
      *self._lines,
      '!',
      'end',
      sep='\n'
    )
    # print('!',self._name)
    # print('\n'.join(map(str,self._lines)))
    # print('stop')
    return

  def _compute_bounds(self):
    lo,hi = 1,1
    for obj in self._objects:
      if isinstance(obj,Structure):
        for load in obj._objects["loads"]:
          if isinstance(load,StepLoad):
            load_min,load_max = load.bounds()
            lo = min(lo,load_min)
            hi = max(hi,load_max)
    return lo,hi

  def timesteps(self,stepsize=1):
    begin,end = self._compute_bounds()
    startiter = range(begin,end,stepsize)
    nextiter  = range(min(begin+stepsize,end),end,stepsize)
    for now,nextit in zip(startiter,nextiter):
      yield now,nextit if nextit-1 == now else nextit-1
    yield nextit,end

  @staticmethod
  def _input_from(stream,strict=False,expand=True):
    if stream in {'display','stdin'}:
      ret = '*input from display'
    else:
      if expand:
        path = resolve_path(stream,strict=strict)
      else:
        path = stream
      ret = f'*input from file \"{path}\"'
    return ret

  def input_from(self,*args,**kwargs):
    self._lines.append(self._input_from(*args,**kwargs))

  def output(self,filename=None):
    if filename is None:
      filename = ''.join(self._name.split())
    self._lines.append(f'output model flat patran convention text file {filename}')
    return
