#!/usr/bin/env python3
"""
# Created: Sun Jan  9 15:19:01 2022 (-0500)
# @author: jacobfaibussowitsch
"""
import os
import sys
import pathlib

class WarpPath(type(pathlib.Path())):
  def resolve(self,*args,**kwargs):
    new_parts = tuple(map(os.path.expandvars,self.parts))
    if new_parts == self.parts:
      return super().resolve(*args,**kwargs)
    return self._from_parts(new_parts).resolve(*args,**kwargs)


def path_cast(path):
  if isinstance(path,WarpPath):
    return path
  if isinstance(path,str):
    return WarpPath(path)
  raise TypeError(type(path))

def resolve_path(path,strict=False):
  path = path_cast(path).expanduser()
  if sys.version_info < (3,6):
    try:
      # pre-3.6 behavior is strict by default
      path = path.resolve()
    except FileNotFoundError:
      if strict:
        raise
    return path
  return path.resolve(strict=strict)

def to_arglist(dictlike,sep=' ',truthy=None,falsey=None):
  if truthy is None:
    truthy = lambda sep,k,v : k

  ret = []
  for k,v in dictlike.items():
    if v is False or v is None:
      if falsey is None:
        continue
      val = falsey(sep,k,v)
    elif v is True:
      val = truthy(sep,k,v)
    else:
      val = sep.join(map(str,(k,v)))
    ret.append(val)
  return ret

def quoted(obj):
  return f'"{obj}"'
