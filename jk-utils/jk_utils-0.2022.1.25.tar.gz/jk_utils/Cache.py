


import os
import sys
import socket
import time
import json
import codecs
import re

from .dtutils import *



class Cache(object):

	def __init__(self, cacheDurationSeconds):
		self.__cacheRecords = {}
		self.__cacheDurationMS = cacheDurationSeconds * 1000

	def put(self, key, value):
		self.__cacheRecords[key] = (dtutils.nowInSecondsSinceEpoch(), value)

	def get(self, key, touch = False):
		r = self.__cacheRecords.get(key, None)
		if r is None:
			return None
		(t, value) = r
		now = dtutils.nowInSecondsSinceEpoch()
		if t + self.__cacheDurationMS < now:
			del self.__cacheRecords[key]
			return None
		if touch:
			self.__cacheRecords[key] = (now, value)
		return value

	def clear(self):
		self.__cacheRecords.clear()

	def cleanup(self):
		keysToDelete = []
		now = dtutils.nowInSecondsSinceEpoch()
		for (key, (t, value)) in self.__cacheRecords.items():
			if t + self.__cacheDurationMS < now:
				keysToDelete.append(key)
		for key in keysToDelete:
			del self.__cacheRecords[key]













