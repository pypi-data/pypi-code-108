#!/usr/bin/python3



import weakref



class WeakRefObservableEvent(object):

	def __init__(self, name = None):
		self.__name = name
		self.__listeners = tuple()
	#

	@property
	def name(self):
		return self.__name
	#

	@property
	def listeners(self):
		return self.__listeners
	#

	def __len__(self):
		return len(self.__listeners)
	#

	def removeAllListeners(self):
		self.__listeners = tuple()
	#

	def __str__(self):
		if self.__name:
			ret = repr(self.__name)[1:][:-1] + "("
		else:
			ret = "Event("
		if len(self.__listeners) == 0:
			ret += "no listener)"
		elif len(self.__listeners) == 1:
			ret += "1 listener)"
		else:
			ret += str(len(self.__listeners)) + " listeners)"
		return ret
	#

	def __repr__(self):
		if self.__name:
			ret = repr(self.__name)[1:][:-1] + "("
		else:
			ret = "Event("
		if len(self.__listeners) == 0:
			ret += "no listener)"
		elif len(self.__listeners) == 1:
			ret += "1 listener)"
		else:
			ret += str(len(self.__listeners)) + " listeners)"
		return ret
	#

	def add(self, theCallable:callable):
		assert theCallable != None
		self.__listeners += (weakref.ref(theCallable),)
		return self
	#

	def __iadd__(self, theCallable:callable):
		assert theCallable != None
		self.__listeners += (weakref.ref(theCallable),)
		return self
	#

	def remove(self, theCallable:callable) -> bool:
		assert theCallable != None
		if theCallable in self.__listeners:
			n = self.__listeners.index(theCallable)
			self.__listeners = self.__listeners[:n] + self.__listeners[n + 1:]
			return True
		else:
			return False
	#

	def _removeAt(self, n:int):
		self.__listeners = self.__listeners[:n] + self.__listeners[n + 1:]
	#

	def __isub__(self, theCallable:callable):
		assert theCallable != None
		if theCallable in self.__listeners:
			n = self.__listeners.index(theCallable)
			self.__listeners = self.__listeners[:n] + self.__listeners[n + 1:]
		return self
	#

	def __call__(self, *argv, **kwargs):
		n = 0
		for listener in self.__listeners:
			o = listener()
			if o:
				o(*argv, **kwargs)
				n += 1
			else:
				self._removeAt(n)
	#

	def fire(self, *argv, **kwargs):
		n = 0
		for listener in self.__listeners:
			o = listener()
			if o:
				o(*argv, **kwargs)
				n += 1
			else:
				self._removeAt(n)
	#

#
