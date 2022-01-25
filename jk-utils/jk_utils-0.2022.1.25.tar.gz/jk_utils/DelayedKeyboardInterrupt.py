


import signal



class DelayedKeyboardInterrupt(object):

	def __init__(self, log, message = "SIGINT received. Delaying keyboard interrupt."):
		self.__bSignalRaised = False
		self.__signal_received = False
		self.__log = log
		self.__message = message
		self.__old_handler = None

	def __enter__(self):
		self.__bSignalRaised = False
		self.__signal_received = False
		self.__old_handler = signal.getsignal(signal.SIGINT)
		signal.signal(signal.SIGINT, self.handler)

	def handler(self, sig, frame):
		self.__signal_received = (sig, frame)
		if self.__message != None:
			self.__log.debug(self.__message)

	def __exit__(self, type, value, traceback):
		signal.signal(signal.SIGINT, self.__old_handler)
		if self.__signal_received:
			self.__old_handler(*self.__signal_received)













