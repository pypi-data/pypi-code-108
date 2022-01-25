



import asyncio
import collections

from asyncio.coroutines import coroutine


class QueueEmpty(Exception):
	"""Exception raised when Queue.get_nowait() is called on a Queue object
	which is empty.
	"""
	pass


class QueueFull(Exception):
	"""Exception raised when the Queue.put_nowait() method is called on a Queue
	object which is full.
	"""
	pass

class QueueFinished(Exception):
	"""Exception raised when the Queue.put_nowait() method is called on a Queue
	object which is already finished.
	"""
	pass

class QueueStopped():
	pass

class Queue:
	"""A queue, useful for coordinating producer and consumer coroutines.

	If maxsize is less than or equal to zero, the queue size is infinite. If it
	is an integer greater than 0, then "yield from put()" will block when the
	queue reaches maxsize, until an item is removed by get().

	Unlike the standard library Queue, you can reliably know this Queue's size
	with qsize(), since your single-threaded asyncio application won't be
	interrupted between calling qsize() and doing an operation on the Queue.
	"""

	STOPPED = QueueStopped()

	def __init__(self, maxsize=0, *, loop=None):
		if loop is None:
			self._loop = asyncio.events.get_event_loop()
		else:
			self._loop = loop
		self._maxsize = maxsize

		# Futures.
		self._getters = collections.deque()
		# Futures.
		self._putters = collections.deque()
		self._bFinished = False
		self._finished = asyncio.locks.Event(loop=self._loop)
		self._init(maxsize)

	# These three are overridable in subclasses.

	def _init(self, maxsize):
		self._queue = collections.deque()

	def _get(self):
		return self._queue.popleft()

	def _put(self, item):
		self._queue.append(item)

	# End of the overridable methods.

	def _wakeup_next(self, waiters):
		# Wake up the next waiter (if any) that isn't cancelled.
		while waiters:
			waiter = waiters.popleft()
			if not waiter.done():
				waiter.set_result(None)
				break

	def __repr__(self):
		return '<{} at {:#x} {}>'.format(
			type(self).__name__, id(self), self._format())

	def __str__(self):
		return '<{} {}>'.format(type(self).__name__, self._format())

	def _format(self):
		result = 'maxsize={!r}'.format(self._maxsize)
		if getattr(self, '_queue', None):
			result += ' _queue={!r}'.format(list(self._queue))
		if self._getters:
			result += ' _getters[{}]'.format(len(self._getters))
		if self._putters:
			result += ' _putters[{}]'.format(len(self._putters))
		return result

	def qsize(self):
		"""Number of items in the queue."""
		return len(self._queue)

	@property
	def maxsize(self):
		"""Number of items allowed in the queue."""
		return self._maxsize

	def empty(self):
		"""Return True if the queue is empty, False otherwise."""
		return not self._queue

	def full(self):
		"""Return True if there are maxsize items in the queue.

		Note: if the Queue was initialized with maxsize=0 (the default),
		then full() is never True.
		"""
		if self._maxsize <= 0:
			return False
		else:
			return self.qsize() >= self._maxsize

	@coroutine
	def put(self, item):
		"""Put an item into the queue.

		Put an item into the queue. If the queue is full, wait until a free
		slot is available before adding item.

		This method is a coroutine.
		"""
		while self.full():
			putter = self._loop.create_future()
			self._putters.append(putter)
			try:
				yield from putter
			except:
				putter.cancel()  # Just in case putter is not done yet.
				if not self.full() and not putter.cancelled():
					# We were woken up by get_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._putters)
				raise
		return self.put_nowait(item)

	def put_nowait(self, item):
		"""Put an item into the queue without blocking.

		If no free slot is immediately available, raise QueueFull.
		"""
		if self._bFinished:
			raise QueueFinished
		if self.full():
			raise QueueFull
		self._put(item)
		self._bFinished = False
		self._finished.clear()
		self._wakeup_next(self._getters)

	@coroutine
	def get(self):
		"""Remove and return an item from the queue.

		If queue is empty, wait until an item is available.

		This method is a coroutine.
		"""
		while self.empty():
			if self._bFinished:
				return AsyncQueue.STOPPED
			getter = self._loop.create_future()
			self._getters.append(getter)
			try:
				yield from getter
			except:
				getter.cancel()  # Just in case getter is not done yet.
				if not self.empty() and not getter.cancelled():
					# We were woken up by put_nowait(), but can't take
					# the call.  Wake up the next in line.
					self._wakeup_next(self._getters)
				raise
		return self.get_nowait()

	def get_nowait(self):
		"""Remove and return an item from the queue.

		Return an item if one is immediately available, else raise QueueEmpty.
		"""
		if self.empty():
			if self._bFinished:
				return AsyncQueue.STOPPED
			raise QueueEmpty
		item = self._get()
		self._wakeup_next(self._putters)
		return item

	def completed(self):
		"""Indicate that producing data is completed.
		"""
		self._finished.set()
		self._bFinished = True

		for i in range(0, len(self._getters)):
			self._wakeup_next(self._getters)

	@coroutine
	def join(self):
		"""Block until all items in the queue have been gotten and processed.

		The count of unfinished tasks goes up whenever an item is added to the
		queue. The count goes down whenever a consumer calls task_done() to
		indicate that the item was retrieved and all work on it is complete.
		When the count of unfinished tasks drops to zero, join() unblocks.
		"""
		yield from self._finished.wait()




