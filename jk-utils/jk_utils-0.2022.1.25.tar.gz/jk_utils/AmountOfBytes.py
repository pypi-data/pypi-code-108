


import typing
import re

from .showCapacityProgress import formatBytes





#
# This class represents a specific amount of bytes. An object of this class is intended to either represent an existing amount of data specified by users,
# by a configuration file or represent data that requires human readable formatting.
#
class AmountOfBytes(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, value):
		self.__n = AmountOfBytes.__parseBytesFromAny(value)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __repr__(self):
		return "AmountOfBytes<(" + AmountOfBytes.__bytesToStrAuto(self.__n) + ")>"
	#

	def __str__(self):
		return AmountOfBytes.__bytesToStrAuto(self.__n)
	#

	#
	# Use this method to retrieve formatted output of the data.
	#
	def toStr(self, bShort:bool = True, magnitude:str = None) -> str:
		if magnitude in "KBMGT":
			return AmountOfBytes.__bytesToStrFixed(self.__n, magnitude)
		elif bShort:
			return formatBytes(self.__n)
		else:
			return AmountOfBytes.__bytesToStrAuto(self.__n)
	#

	def __float__(self):
		return float(self.__n)
	#

	def __int__(self):
		return self.__n
	#

	def __add__(self, other):
		if isinstance(other, AmountOfBytes):
			return AmountOfBytes(self.__n + other.__n)
		elif isinstance(other, int):
			return AmountOfBytes(self.__n + other)
		elif isinstance(other, float):
			return self.__n + other
		else:
			raise TypeError(repr(other))
	#

	def __sub__(self, other):
		if isinstance(other, AmountOfBytes):
			return AmountOfBytes(self.__n - other.__n)
		elif isinstance(other, int):
			return AmountOfBytes(self.__n - other)
		elif isinstance(other, float):
			return self.__n - other
		else:
			raise TypeError(repr(other))
	#

	def __mul__(self, other):
		if isinstance(other, AmountOfBytes):
			raise TypeError(repr(other))
		elif isinstance(other, int):
			return AmountOfBytes(self.__n * other)
		elif isinstance(other, float):
			return self.__n * other
		else:
			raise TypeError(repr(other))
	#

	def __div__(self, other):
		if isinstance(other, AmountOfBytes):
			raise TypeError(repr(other))
		elif isinstance(other, int):
			return self.__n / other
		elif isinstance(other, float):
			return self.__n / other
		else:
			raise TypeError(repr(other))
	#

	def __eq__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n == other.__n
		elif isinstance(other, int):
			return self.__n == other
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n != other.__n
		elif isinstance(other, int):
			return self.__n != other
		else:
			return False
	#

	def __gt__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n > other.__n
		elif isinstance(other, (int, float)):
			return self.__n > other
		else:
			return False
	#

	def __ge__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n >= other.__n
		elif isinstance(other, (int, float)):
			return self.__n >= other
		else:
			return False
	#

	def __lt__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n < other.__n
		elif isinstance(other, (int, float)):
			return self.__n < other
		else:
			return False
	#

	def __le__(self, other):
		if isinstance(other, AmountOfBytes):
			return self.__n <= other.__n
		elif isinstance(other, (int, float)):
			return self.__n <= other
		else:
			return False
	#

	################################################################################################################################
	## Static Helper Methods
	################################################################################################################################

	@staticmethod
	def __parseBytesFromAny(v:typing.Union[int,str]) -> int:
		if isinstance(v, int):
			assert v >= 0
			return v

		vText = v.strip().upper()

		m = re.match("^([0-9.]+)\s*([KMGT]B?)$", vText)
		if m:
			try:
				n = float(m.group(1))
			except:
				raise Exception("Value does not specify bytes: " + repr(vText))

			sFactor = m.group(2)
			if sFactor.startswith("K"):
				n *= 1024
			elif sFactor.startswith("M"):
				n *= 1024*1024
			elif sFactor.startswith("G"):
				n *= 1024*1024*1024
			elif sFactor.startswith("T"):
				n *= 1024*1024*1024*1024
			else:
				pass

			return int(n)

		else:
			try:
				return int(vText)
			except Exception as ee:
				raise Exception("Value does not specify bytes: " + repr(vText))
	#

	@staticmethod
	def __bytesToStrAuto(n:int) -> str:
		if (n >= 1024*1024*1024*1024) and ((n % (1024*1024*1024*1024)) == 0):
			return str(n // (1024*1024*1024*1024)) + "T"
		elif (n >= 1024*1024*1024) and ((n % (1024*1024*1024)) == 0):
			return str(n // (1024*1024*1024)) + "G"
		elif (n >= 1024*1024) and ((n % (1024*1024)) == 0):
			return str(n // (1024*1024)) + "M"
		elif (n >= 1024) and ((n % 1024) == 0):
			return str(n // 1024) + "K"
		else:
			return str(n)
	#

	@staticmethod
	def __bytesToStrFixed(n:int, mag:str) -> str:
		if mag == "T":
			v = round(n / (1024*1024*1024*1024), 2)
		elif mag == "G":
			v = round(n / (1024*1024*1024), 2)
		elif mag == "M":
			v = round(n / (1024*1024), 2)
		elif mag == "K":
			v = round(n / 1024, 1)
		else:
			v = n

		return str(v) + " " + mag
	#

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	@staticmethod
	def parseFromStr(v:str):
		assert isinstance(v, str)
		return AmountOfBytes(v)
	#

	@staticmethod
	def parse(v:typing.Union[int,str]):
		assert isinstance(v, (int,str))
		return AmountOfBytes(v)
	#

#














