#!/usr/bin/env python3
"""
# Created: Sun Jan  9 14:15:18 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import collections
from ._warpobject import WarpObjectBase
from ._util import to_arglist

class Material(WarpObjectBase):
  _typename = 'material'

  def __init__(self,model,name,*args,**kwargs):
    __doc__="""
    Define a material

    Parameters
    ----------
    name : name of the material, convertable to string

    model : list of constitutive models of the material
    """
    super().__init__(name)
    self._model      = list(map(str,args))
    self._properties = collections.OrderedDict(**kwargs)
    model._add_object(self)
    return

  def _finalize(self):
    arg_list = to_arglist(self._properties)
    return [
      f'properties {" ".join(self._model)},',
      [a+',' for a in arg_list[:-1]]+[arg_list[-1]]
    ]

  def set_properties(self,**kwargs):
    self._properties.update(**kwargs)
    return
