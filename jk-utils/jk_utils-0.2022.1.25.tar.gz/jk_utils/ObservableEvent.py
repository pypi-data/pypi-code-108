#!/usr/bin/python3




class _LockCtx(object):

	__slots__ = ( "__evt", "__bPreventFiringOnUnlock" )

	def __init__(self, evt, bPreventFiringOnUnlock:bool = False):
		self.__evt = evt
		self.__bPreventFiringOnUnlock = bPreventFiringOnUnlock
	#

	def dump(self):
		print("_LockCtx(")
		print("\t__evt = " + str(self.__evt))
		print("\t__bPreventFiringOnUnlock = " + str(self.__bPreventFiringOnUnlock))
		print(")")
	#

	def preventFiringOnUnlock(self):
		self.__bPreventFiringOnUnlock = True
	#

	def __enter__(self):
		return self
	#

	def __exit__(self, exType, exObj, traceback):
		self.__evt.unlock(bPreventFiring = self.__bPreventFiringOnUnlock or (exType is not None))
	#

#




class ObservableEvent(object):

	def __init__(self, name:str = None, bCatchExceptions:bool = False):
		self.__name = name
		self.__listeners = tuple()
		self.__bCatchExceptions = bCatchExceptions
		self.__lockCounter = 0
		self.__bNeedFiring = False
		self.__lockCtx = None
	#

	@property
	def catchExceptions(self):
		return self.__bCatchExceptions
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
			ret += "no listener"
		elif len(self.__listeners) == 1:
			ret += "1 listener"
		else:
			ret += str(len(self.__listeners)) + " listeners"

		if self.__lockCounter > 0:
			ret += ", lockCounter=" + str(self.__lockCounter)
			if self.__bNeedFiring:
				ret += ", fire on unlock"

		return ret + ")"
	#

	def __repr__(self):
		return self.__str__()
	#

	def add(self, theCallable:callable):
		assert theCallable != None
		self.__listeners += (theCallable,)
		return self
	#

	def __iadd__(self, theCallable:callable):
		assert theCallable != None
		self.__listeners += (theCallable,)
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

	def __isub__(self, theCallable:callable):
		assert theCallable != None
		if theCallable in self.__listeners:
			n = self.__listeners.index(theCallable)
			self.__listeners = self.__listeners[:n] + self.__listeners[n + 1:]
			return True
		else:
			return False
	#

	def __call__(self, *argv, **kwargs):
		if self.__bCatchExceptions:
			try:
				for listener in self.__listeners:
					listener(*argv, **kwargs)
			except Exception as ee:
				pass
		else:
			for listener in self.__listeners:
				listener(*argv, **kwargs)
	#

	def fire(self, *argv, **kwargs):
		if self.__lockCounter > 0:
			self.__bNeedFiring = True

		else:
			self.__bNeedFiring = False

			if self.__bCatchExceptions:
				try:
					for listener in self.__listeners:
						listener(*argv, **kwargs)
				except Exception as ee:
					pass
			else:
				for listener in self.__listeners:
					listener(*argv, **kwargs)
	#

	def lock(self):
		self.__lockCounter += 1
		if self.__lockCtx is None:
			self.__lockCtx = _LockCtx(self)
		return self.__lockCtx
	#

	def unlock(self, bPreventFiring:bool = False):
		assert self.__lockCounter > 0
		self.__lockCounter -= 1
		if self.__bNeedFiring:
			if bPreventFiring:
				self.__bNeedFiring = False
			else:
				self.fire()
	#

#
