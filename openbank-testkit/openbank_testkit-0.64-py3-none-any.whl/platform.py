#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


class staticproperty(staticmethod):
  def __get__(self, *args):
    return self.__func__()


class Platform(object):

  __instance = None

  @staticmethod 
  def __lazy():
    if Platform.__instance == None:
      Platform()
    return Platform.__instance

  def __init__(self):
    if Platform.__instance == None:
      self.__arch = {
        'arm64': 'arm64',
        'amd64': 'amd64',
        'x86_64': 'amd64',
        'armv8': 'arm64',
        'aarch64': 'arm64'
      }.get(os.uname().machine, 'amd64')
      Platform.__instance = self

  @staticproperty
  def arch():
    return Platform.__lazy().__arch
