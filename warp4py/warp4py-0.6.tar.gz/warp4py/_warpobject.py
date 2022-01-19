#!/usr/bin/env python3
"""
# Created: Fri Jan 14 14:09:22 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import collections

class WarpObjectBase(object):
  __slots__ = "_name"

  def __init__(self,name=None):
    if name is None:
      name = self._typename
    self._name = str(name)
    return

  def __hash__(self):
    return hash(self._name)

  def __str__(self):
    def iterable(arg):
      return isinstance(arg,collections.Iterable) and not isinstance(arg,str)

    def push_tab(line_list,tab_level=0):
      line_list = [
        push_tab(l,tab_level=tab_level+1) if iterable(l) else l for l in line_list
      ]
      tabs      = '  '*tab_level
      return '\n'.join(l if l.startswith(' ') else tabs+l for l in line_list)

    if self._name == self._typename:
      init = f'{self._typename}'
    else:
      init = f'{self._typename} {self._format_name()}'
    final = self._finalize()
    if isinstance(final,str):
      return '!\n'+' '.join((init,final))
    else:
      return '!\n'+push_tab([init,self._finalize()])

  def _format_name(self):
    return self._name
