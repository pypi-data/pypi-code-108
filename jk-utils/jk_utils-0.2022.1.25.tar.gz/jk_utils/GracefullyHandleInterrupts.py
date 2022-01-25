

import signal



class GracefullyHandleInterrupts(object):

	def __init__(self, log, bCatchSigInt = True, bCatchSigTerm = True,
		messageSigInt = "SIGINT received. Terminating gracefuly ...",
		messageSigTerm = "SIGINT received. Terminating gracefuly ..."):

		self.__bSignalRaised = False
		self.__signal_received = False
		self.__log = log
		self.__messageSigInt = messageSigInt
		self.__messageSigTerm = messageSigTerm
		self.__bCatchSigInt = bCatchSigInt
		self.__bCatchSigTerm = bCatchSigTerm
		self.__old_handler_sigint = None
		self.__old_handler_sigterm = None

	def __enter__(self):
		self.__bSignalRaised = False
		self.__signal_received = False
		if self.__bCatchSigInt:
			self.__old_handler_sigint = signal.getsignal(signal.SIGINT)
			signal.signal(signal.SIGINT, self.handler)
		if self.__bCatchSigTerm:
			self.__old_handler_sigterm = signal.getsignal(signal.SIGTERM)
			signal.signal(signal.SIGTERM, self.handler)

	def handler(self, sig, frame):
		self.__signal_received = (sig, frame)
		if sig == signal.SIGINT:
			if self.__messageSigInt != None:
				self.__log.info(self.__messageSigInt)
		elif sig == signal.SIGTERM:
			if self.__bCatchSigTerm != None:
				self.__log.info(self.__bCatchSigTerm)
		else:
			self.__log.error("Implementation error!")

	def __exit__(self, type, value, traceback):
		if self.__bCatchSigInt:
			signal.signal(signal.SIGINT, self.__old_handler_sigint)
		if self.__bCatchSigTerm:
			signal.signal(signal.SIGTERM, self.__old_handler_sigterm)

	@property
	def isInterrupted(self):
		return self.__signal_received != False











