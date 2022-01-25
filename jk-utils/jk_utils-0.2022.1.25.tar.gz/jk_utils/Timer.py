


import time
import threading



from .ObservableEvent import ObservableEvent



#
# TODO: Make the timing more accurate by using a more precise sleep time!
#
class Timer(object):

	def __init__(self, delaySeconds:int):
		self.__bKeepRunning = True
		self.__delaySeconds = delaySeconds
		self.__onTimerEvent = ObservableEvent("timerTick")
		self.__onErrorEvent = ObservableEvent("timerError", bCatchExceptions=True)

		self.__thread = threading.Thread(target=self.__runTimer, daemon=True)
		self.__thread.start()
	#

	def __del__(self):
		self.__bKeepRunning = False
	#

	@property
	def onTimer(self):
		return self.__onTimerEvent
	#

	@property
	def onError(self):
		return self.__onErrorEvent
	#

	def __runTimer(self):
		while self.__bKeepRunning:
			time.sleep(self.__delaySeconds)
			try:
				self.__onTimerEvent(self)
			except Exception as ee:
				self.__onErrorEvent(ee)

		self.__thread = None
	#

	def terminate(self):
		self.__bKeepRunning = False
	#

#








