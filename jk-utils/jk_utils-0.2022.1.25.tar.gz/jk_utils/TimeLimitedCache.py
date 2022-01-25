
import time
import threading
from typing import Union

import sortedcontainers





class _TimeLimitedCacheEntry(object):

	def __init__(self, identifier, deathTime:float, data):
		self.identifier = identifier
		self.deathTime = deathTime
		self.data = data
	#

#



def _getCEKey(item):
	return item.deathTime
#



#
# This class provides a cache that drops out items after a certain amount of time.
# Checks if data in the cache is obsolete is performed on every call of <c>put()</c>, <c>get()</c> and <c>remove()</c>.
# (If required by technical demands, this might be changed in the future.)
#
class TimeLimitedCache(object):

	def __init__(self, secondsToLive:Union[int,float]):
		assert isinstance(secondsToLive, (int, float))
		assert secondsToLive > 0

		self.__entriesByDeathTime = sortedcontainers.SortedListWithKey(key=_getCEKey)
		self.__entriesByID = dict()
		self.__secondsToLive = secondsToLive

		self.__lock = threading.Lock()
	#

	def __tryClean(self, tNow):
		while len(self.__entriesByDeathTime) > 0:
			existingEntry = self.__entriesByDeathTime[0]
			if existingEntry.deathTime > tNow:
				break
			else:
				self.__entriesByDeathTime.remove(existingEntry)
				del self.__entriesByID[existingEntry.identifier]
	#

	def put(self, identifier, item):
		assert isinstance(identifier, (str, int))

		tNow = time.time()

		newEntry = _TimeLimitedCacheEntry(identifier, tNow + self.__secondsToLive, item)

		self.__lock.acquire()

		existingEntry = self.__entriesByID.get(identifier, None)
		if existingEntry:
			self.__entriesByDeathTime.remove(existingEntry)
			del self.__entriesByID[identifier]

		self.__tryClean(tNow)

		self.__entriesByDeathTime.add(newEntry)
		self.__entriesByID[identifier] = newEntry

		self.__lock.release()
	#

	def get(self, identifier, bTouch:bool = True):
		assert isinstance(identifier, (str, int))
		assert isinstance(bTouch, bool)

		tNow = time.time()

		self.__lock.acquire()

		if bTouch:

			existingEntry = self.__entriesByID.get(identifier, None)
			if existingEntry:
				self.__entriesByDeathTime.remove(existingEntry)
				existingEntry.deathTime = tNow + self.__secondsToLive
				self.__entriesByDeathTime.add(existingEntry)

			self.__tryClean(tNow)

		else:

			self.__tryClean(tNow)
			existingEntry = self.__entriesByID.get(identifier, None)

		self.__lock.release()

		return None if existingEntry is None else existingEntry.data
	#

	def remove(self, identifier):
		assert isinstance(identifier, (str, int))

		self.__lock.acquire()

		existingEntry = self.__entriesByID.get(identifier, None)
		if existingEntry:
			self.__entriesByDeathTime.remove(existingEntry)
			del self.__entriesByID[identifier]

		self.__tryClean(time.time())

		self.__lock.release()
	#

#

























