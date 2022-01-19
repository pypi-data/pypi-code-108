#!/usr/bin/env python3
"""
# Created: Sun Jan  9 18:34:29 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import abc
import collections

from ._warpobject import WarpObjectBase
from ._util       import to_arglist
from ._util       import quoted

class ListBase(abc.ABC,WarpObjectBase):
  _typename = 'list'

  def __init__(self,struct,name,display=False,coords=False):
    super().__init__(name)
    self._display     = display
    self._coordinates = coords
    struct._add_object(self)
    return

  def _finalize(self):
    items = collections.OrderedDict()
    items['display']     = self._display
    items['coordinates'] = self._coordinates
    return ' '.join(self._get_lines()+to_arglist(items))

  def _format_name(self):
    return quoted(self._name)

  @abc.abstractmethod
  def _get_lines(self):
    raise NotImplementedError

class GeometricList(ListBase):
  def __init__(self,*args,x=None,y=None,z=None,tolerance=None,**kwargs):
    super().__init__(*args,**kwargs)
    self.items = collections.OrderedDict()
    self.items['x'] = x
    self.items['y'] = y
    self.items['z'] = z
    self.items['tolerance'] = tolerance
    return

  def _get_lines(self):
    return [' '.join(to_arglist(self.items,sep=' = '))]
