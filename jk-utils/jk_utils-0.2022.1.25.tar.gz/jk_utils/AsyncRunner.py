import time
import threading
from typing import Union

import sortedcontainers





class AsyncActivityRecord(object):

	def __init__(self, identifier, timeToRun:float, theCallable:callable, callArguments:Union[tuple,list], autoRescheduleDelay:Union[int,float] = 0):
		self.identifier = identifier
		self.timeToRun = timeToRun
		self.theCallable = theCallable
		self.callArguments = callArguments
		self.autoRescheduleDelay = autoRescheduleDelay
	#

#



def _getARKey(item):
	return item.timeToRun
#



class AsyncRunner(object):

	def __init__(self, debugLogPrintFunction:callable = None):
		# list of all activities
		self.__activitiesByTime = sortedcontainers.SortedListWithKey(key=_getARKey)
		# list of activities that later can be identified again
		self.__activitiesByID = dict()
		self.__debugLogPrintFunction = debugLogPrintFunction
		self.__lock = threading.Lock()
		self.__evt = threading.Event()
		self.__thread = threading.Thread(target=self.__run, daemon=True)
		self.__bKeepRunning = True
		self.__bRunning = True
		self.__bIsStarted = False
	#

	def start(self):
		if self.__bIsStarted:
			if self.__bRunning:
				return True
			else:
				return False
		else:
			self.__bIsStarted = True
			self.__thread.start()
			return True
	#

	def __del__(self):
		if self.__bRunning:
			self.stop()
	#

	def __run(self):
		if self.__debugLogPrintFunction:
			self.__debugLogPrintFunction("[AsyncRunner] Thread started.")

		timeToWait = None
		while self.__bKeepRunning:
			if self.__debugLogPrintFunction:
				self.__debugLogPrintFunction("[AsyncRunner] Queue length is " + str(len(self.__activitiesByTime)) + ". Waiting.")

			self.__evt.wait(timeToWait)

			tNow = time.time()
			while True:

				if self.__debugLogPrintFunction:
					self.__debugLogPrintFunction("[AsyncRunner] Queue length is " + str(len(self.__activitiesByTime)) + ". Checking.")

				# get top most activity
				self.__lock.acquire()
				if len(self.__activitiesByTime) > 0:
					# activity found; remove it;
					topMostActivity = self.__activitiesByTime[0]
					self.__activitiesByTime.remove(topMostActivity)
					if topMostActivity.identifier != None:
						del self.__activitiesByID[topMostActivity.identifier]
					if self.__debugLogPrintFunction:
						self.__debugLogPrintFunction("[AsyncRunner] Retrieving from queue: " + str(topMostActivity))
				else:
					topMostActivity = None
				self.__lock.release()

				if topMostActivity:
					# we have another activity
					if topMostActivity.timeToRun <= tNow:
						# activity is scheduled to run now!
						if self.__debugLogPrintFunction:
							self.__debugLogPrintFunction("[AsyncRunner] Activitiy to run: " + str(topMostActivity))

						if topMostActivity.autoRescheduleDelay > 0:
							# reschedule the activity

							if self.__debugLogPrintFunction:
								self.__debugLogPrintFunction("[AsyncRunner] Reinserting to run in " + str(topMostActivity.autoRescheduleDelay) + " seconds: " + str(topMostActivity))
							topMostActivity.timeToRun = tNow + topMostActivity.autoRescheduleDelay

							self.__lock.acquire()
							self.__activitiesByTime.add(topMostActivity)
							if topMostActivity.identifier != None:
								self.__activitiesByID[topMostActivity.identifier] = topMostActivity
							self.__lock.release()

						# now run the activity
						if self.__debugLogPrintFunction:
							self.__debugLogPrintFunction("[AsyncRunner] Now running: " + str(topMostActivity))
						topMostActivity.theCallable(topMostActivity.callArguments)
					else:
						# wait
						timeToWait = topMostActivity.timeToRun - tNow

						if self.__debugLogPrintFunction:
							self.__debugLogPrintFunction("[AsyncRunner] Reinserting to run in " + str(timeToWait) + " seconds: " + str(topMostActivity))

						self.__lock.acquire()
						self.__activitiesByTime.add(topMostActivity)
						if topMostActivity.identifier != None:
							self.__activitiesByID[topMostActivity.identifier] = topMostActivity
						self.__lock.release()

						break
				else:
					# no more activities waiting
					timeToWait = None
					if self.__debugLogPrintFunction:
						self.__debugLogPrintFunction("[AsyncRunner] Queue is empty.")
					break

		if self.__debugLogPrintFunction:
			self.__debugLogPrintFunction("[AsyncRunner] Thread terminated.")

		self.__bRunning = False
	#

	def stop(self):
		self.__bKeepRunning = False
		self.__evt.set()
		self.__evt.clear()
	#

	def rescheduleCallable(self, theCallable:callable, callArguments:Union[tuple,list], delaySeconds:Union[int,float],
		identifier:Union[str,int,None] = None, autoRescheduleDelay:Union[int,float] = 0):

		assert callable(theCallable)
		assert isinstance(delaySeconds, (int, float))
		assert delaySeconds >= 0
		assert isinstance(autoRescheduleDelay, (int, float))

		if identifier is None:
			identifier = id(theCallable)
		else:
			isinstance(identifier, (str, int))

		timeToRun = time.time() + delaySeconds

		if self.__debugLogPrintFunction:
			self.__debugLogPrintFunction("[AsyncRunner] (re)scheduling activity to run in " + str(delaySeconds) + " seconds: " + str(theCallable) + ", " + repr(callArguments))

		self.__lock.acquire()
		existingActivity = self.__activitiesByID.get(identifier, None)
		if existingActivity:
			self.__activitiesByTime.remove(existingActivity)
			existingActivity.timeToRun = timeToRun
			existingActivity.theCallable = theCallable
			existingActivity.callArguments = callArguments
			self.__activitiesByTime.add(existingActivity)
		else:
			newActivity = AsyncActivityRecord(identifier, timeToRun, theCallable, callArguments, autoRescheduleDelay)
			self.__activitiesByTime.add(newActivity)
			self.__activitiesByID[identifier] = newActivity
		self.__lock.release()

		self.__evt.set()
		self.__evt.clear()
	#

	def removeScheduledCallable(self, identifier:Union[str,int]):
		isinstance(identifier, (str, int))

		self.__lock.acquire()
		existingActivity = self.__activitiesByID.get(identifier, None)
		if existingActivity:
			self.__activitiesByTime.remove(existingActivity)
			del self.__activitiesByID[identifier]

			if self.__debugLogPrintFunction:
				self.__debugLogPrintFunction("[AsyncRunner] Removed: " + str(existingActivity))
		self.__lock.release()
	#

	def scheduleCallable(self, theCallable:callable, callArguments:Union[tuple,list], delaySeconds:Union[int,float] = 0,
		autoRescheduleDelay:Union[int,float] = 0):

		assert callable(theCallable)
		assert isinstance(delaySeconds, (int, float))
		assert delaySeconds >= 0
		assert isinstance(autoRescheduleDelay, (int, float))

		timeToRun = time.time() + delaySeconds

		if self.__debugLogPrintFunction:
			self.__debugLogPrintFunction("[AsyncRunner] scheduling activity to run in " + str(delaySeconds) + " seconds: " + str(theCallable) + ", " + repr(callArguments))

		newActivity = AsyncActivityRecord(None, timeToRun, theCallable, callArguments, autoRescheduleDelay)
		self.__lock.acquire()
		self.__activitiesByTime.add(newActivity)
		self.__lock.release()

		self.__evt.set()
		self.__evt.clear()
	#

#










