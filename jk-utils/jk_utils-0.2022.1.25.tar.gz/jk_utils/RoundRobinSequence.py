#!/usr/bin/python3




#
# This is a round-robin sequence. It internally uses a list of fixed length and insertes items in a round-robin fashion, overwriting old items as necessary.
#
class RoundRobinSequence(object):

	def __init__(self, maxLength:int):
		self.__items = [ None ] * maxLength
		self.__startI = 0
		self.__endI = 0
		self.__maxLength = maxLength
		self.__count = 0
	#

	@property
	def maxLength(self):
		return self.__maxLength
	#

	@property
	def count(self):
		return self.__count
	#

	def __len__(self):
		return self.__count
	#

	def __iter__(self):
		if self.__count > 0:
			if self.__startI < self.__endI:
				for i in range(self.__startI, self.__endI):
					yield self.__items[i]
			else:
				for i in range(self.__startI, self.__maxLength):
					yield self.__items[i]
				for i in range(0, self.__endI):
					yield self.__items[i]
	#

	def __getitem__(self, index:int):
		if self.__count:
			assert isinstance(index, int)
			n = (self.__startI + index) % self.__count
			return self.__items[n]
		else:
			raise IndexError()
	#

	def add(self, item):
		self.__items[self.__endI] = item

		self.__endI += 1
		if self.__endI == self.__maxLength:
			self.__endI = 0

		if self.__count == self.__maxLength:
			self.__startI += 1
			if self.__startI == self.__maxLength:
				self.__startI = 0
		else:
			self.__count += 1

		return self
	#

	def addRange(self, iterable):
		for item in iterable:
			self.__items[self.__endI] = item

			self.__endI += 1
			if self.__endI == self.__maxLength:
				self.__endI = 0

			if self.__count == self.__maxLength:
				self.__startI += 1
				if self.__startI == self.__maxLength:
					self.__startI = 0
			else:
				self.__count += 1

		return self
	#

	def items(self):
		if self.__count == 0:
			return []

		if self.__startI < self.__endI:
			return self.__items[self.__startI:self.__endI]
		else:
			return self.__items[self.__startI:] + self.__items[:self.__endI]
	#

	def sum(self):
		if self.__count == 0:
			return 0

		if self.__startI < self.__endI:
			return sum(self.__items[self.__startI:self.__endI])
		else:
			return sum(self.__items[self.__startI:]) + sum(self.__items[:self.__endI])
	#

	def avg(self):
		if self.__count == 0:
			return None

		if self.__startI == self.__endI:
			totalSum = sum(self.__items)
		elif self.__startI < self.__endI:
			totalSum = sum(self.__items[self.__startI:self.__endI])
		else:
			totalSum = sum(self.__items[self.__startI:]) + sum(self.__items[:self.__endI])
		return totalSum / self.__count
	#

	def min(self):
		if self.__count == 0:
			return None

		if self.__startI == self.__endI:
			return min(self.__items)
		elif self.__startI < self.__endI:
			return min(self.__items[self.__startI:self.__endI])
		else:
			a = min(self.__items[self.__startI:])
			b = min(self.__items[:self.__endI])
			return a if a < b else b
	#

	def max(self):
		if self.__count == 0:
			return None

		if self.__startI == self.__endI:
			return max(self.__items)
		elif self.__startI < self.__endI:
			return max(self.__items[self.__startI:self.__endI])
		else:
			a = max(self.__items[self.__startI:])
			if self.__endI > 0:
				b = max(self.__items[:self.__endI])
			return a if a > b else b
	#

#





