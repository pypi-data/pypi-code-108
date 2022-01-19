#!/usr/bin/env python3
"""
# Created: Sun Jan  9 15:32:57 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import abc
from ._warpobject import WarpObjectBase
from ._util import to_arglist

class LoadingBase(abc.ABC,WarpObjectBase):
  _typename = 'loading'

  def __init__(self,struct,name):
    super().__init__(name)
    struct._add_object(self)
    return

  def _finalize(self):
    return [self.modifier(),self._get_lines()]

  @abc.abstractmethod
  def modifier(self):
    raise NotImplementedError

  @abc.abstractmethod
  def _get_lines(self):
    raise NotImplementedError


class NodalLoad(LoadingBase):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    raise NotImplementedError
    return

  def typename(self):
    return

  def finalize(self,prefix):
    return


class ElementLoad(LoadingBase):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    raise NotImplementedError
    return

  def typename(self):
    return

  def finalize(self,prefix):
    return


class StepLoad(LoadingBase):
  def __init__(self,*args,**kwargs):
    super().__init__(*args,**kwargs)
    self._lines = []
    return

  @staticmethod
  def modifier():
    return 'nonlinear'

  def _get_lines(self):
    return [f'steps {b}-{e} {" ".join(to_arglist(rest))}' for b,e,rest in sorted(self._lines)]

  def append(self,end,**kwargs):
    if not self._lines:
      begin = 1
    else:
      begin = self._lines[-1][1]+1
    self._lines.append((begin,end,kwargs))
    return

  def bounds(self):
    if not self._lines:
      return 0,0
    return self._lines[0][0],self._lines[-1][1]


class Constraint(WarpObjectBase):
  _typename = 'constraints'

  def __init__(self,struct):
    super().__init__()
    struct._add_object(self)
    self._lines = []
    return

  def _finalize(self):
    return [f'{t} {" ".join(to_arglist(rest,sep=" = "))}' for t,rest in self._lines]

  def append(self,target,**kwargs):
    self._lines.append((target,kwargs))
    return
