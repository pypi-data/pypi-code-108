#!/usr/bin/env python3

from queue import Queue, Empty

class Conduit(object):
	"""@brief A generalised conduit implementation. A conduit is used for 
	          communication between two processes. Each Conduit has an A 
	          and a B end. Messages can be pushed into each end and 
	          pulled from each end.	
	"""
	CONDUIT_TYPE_QUEUE 			= 1
	CONDUIT_TYPE_TCP_CONNECTION = 2
	
	def __init__(self, uio=None, cName="", conduitType=CONDUIT_TYPE_QUEUE, readBlock=True, readBlockTimeoutSeconds=None, maxSize = 0, ):
		"""@brief Responsible for providing a conduit for data between entities. 
		   @param uio A User input/output object. If supplied then debug info for the conduit will be recorded.
		   @param cName The conduit name. Only useful if a uio object has been passed for debugging purposes.
		   @param readBlock If true then all getX() methods will block until data is available.
		   @param readBlockTimeoutSeconds The time in seconds for a read (when readBlock=True) to timeout. The default = None (block indefinatley).
		   @param maxSize Maximum number of elements in the queue. Only valid if conduitType = CONDUIT_TYPE_QUEUE."""
		
		if conduitType == Conduit.CONDUIT_TYPE_QUEUE:
			self._conduit = QueueConduit(uio=uio, cName=cName, maxQueueSize=maxSize, readBlock=readBlock, readBlockTimeoutSeconds=readBlockTimeoutSeconds)
			
		elif conduitType == Conduit.CONDUIT_TYPE_TCP_CONNECTION:
			raise Exception("TCP conduits not yet implemented.")
		
		else:
			raise Exception("%d is an invalid conduit type." % (conduitType) )
			
	def putA(self, data):
		"""@brief put some data in the A -> B side conduit.
    	   @param data The data object to be pushed into the conduit."""
		self._conduit.putA(data)
    	
	def putB(self, data):
		"""@brief put some data in the B -> A side conduit.
    	   @param data The data object to be pushed into the conduit."""
		self._conduit.putB(data)
    	
	def getA(self):
		"""@brief Get some data from the B -> A conduit.
		   @return The data from the conduit or None of no data is available."""
		return self._conduit.getA()
						
	def getB(self):
		"""@brief Get some data from the A -> B conduit.
		   @return The data from the conduit or None of no data is available."""
		return self._conduit.getB()
		
	def aReadAvailable(self):
		"""@return True if there is data available to be read from the A side of the conduit."""
		return self._conduit.aReadAvailable()

	def bReadAvailable(self):
		"""@return True if there is data available to be read from the B side of the conduit."""
		return self._conduit.bReadAvailable()

class QueueConduit(Conduit):
	"""@brief Responsible for providing the functionality required to communicate between
	          threads (ITC= Inter Thread Communication).
	          
	          The ITC has an A side and a B side. data can be sent from the A and B sides
	          and is forwarded to the other side."""

	def __init__(self, uio=None, cName="", maxQueueSize = 0, readBlock=True, readBlockTimeoutSeconds=0):
		"""@brief Constructor
		   @param uio A User input/output object. If supplied then debug info for the conduit will be recorded.
		   @param cName The conduit name. Only useful if a uio object has been passed for debugging purposes.
		   @param maxQueueSize The maximum queue size that we will allow (default = 0, no limit)
		   @param readBlock If True then reads will block until data is available or a timeout (if > 0) occurs."""
		  
		self._uio = uio
		self._cName = cName
		self._maxQueueSize 				= maxQueueSize
		self._readBlock     			= readBlock
		self._readBlockTimeoutSeconds 	= readBlockTimeoutSeconds
		self._aToBQueue 				= Queue(maxQueueSize)
		self._bToAQueue	 				= Queue(maxQueueSize)
		
	def _checkQueueSize(self):
		"""@brief check that we have not reached the max queue size."""
		if self._maxQueueSize > 0:
			if self._aToBQueue.qsize() >= self._maxQueueSize:
				raise Exception("%s: A -> B queue full." % (self.__class__.__name__) )
				
			if self._bToAQueue.qsize() >= self._maxQueueSize:
				raise Exception("%s: B -> A queue full." % (self.__class__.__name__) )
	
	def putA(self, data):
		"""@brief put some data in the A -> B side queue.
    	   @param data The data object to be pushed into the queue."""
		self._checkQueueSize()
		
		if self._uio:
			qSize = self._aToBQueue.qsize()
			self._uio.debug("%s: A -> B queue size = %d" % (self._cName, qSize) )
		
		self._aToBQueue.put(data)
    	
	def putB(self, data):
		"""@brief put some data in the B -> A side queue.
    	   @param data The data object to be pushed into the queue."""
		self._checkQueueSize()
		
		if self._uio:
			qSize = self._bToAQueue.qsize()
			self._uio.debug("%s: B -> A queue size = %d" % (self._cName, qSize) )
		
		self._bToAQueue.put(data)
    	
	def getA(self, block=True, timeoutSeconds=0.0):
		"""@brief Get some data from the B -> A queue.
		   @param block If true then the call will block
		   @param timeoutSeconds The time in seconds before exiting (returning None) if no data can be read from the queue.
		   @return The data from the queue or None of no data is available."""
		try:
			return self._bToAQueue.get(block=self._readBlock, timeout=self._readBlockTimeoutSeconds)
		except Empty:
			return None
						
	def getB(self, block=True, timeoutSeconds=0.0):
		"""@brief Get some data from the A -> B queue.
		   @param block If true then the call will block
		   @param timeoutSeconds The time in seconds before exiting (returning None) if no data can be read from the queue.
		   @return The data from the queue or None of no data is available."""
		try:
			return self._aToBQueue.get(block=self._readBlock, timeout=self._readBlockTimeoutSeconds)
		except Empty:
			return None
		
	def aReadAvailable(self):
		"""@return True if there is data available to be read from the A side of the queue."""
		return not self._bToAQueue.empty()
	
	def bReadAvailable(self):
		"""@return True if there is data available to be read from the B side of the queue."""
		return not self._aToBQueue.empty()
		   
	
	


			
    	