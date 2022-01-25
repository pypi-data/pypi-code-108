


from .RGB import RGB




class RGBSpectrum(object):

	def __init__(self, rgbValues:list):
		self.__values = rgbValues
	#

	def length(self) -> int:
		return len(self.__values)
	#

	def __len__(self) -> int:
		return len(self.__values)
	#

	def getRange(self, nStart:int, nEnd:int):
		return self.__values[nStart:nEnd]
	#

	def getE(self, n:int):
		return self.__values[n]
	#

	def getN(self, n:int):
		if (n < 0) or (n >= len(self.__values)):
			return None
		return self.__values[n]
	#

	def get(self, n:int):
		if n < 0:
			n = 0
		if n >= len(self.__values):
			n = len(self.__values) - 1
		return self.__values[n]
	#

	def __iter__(self):
		return self.__values.__iter__()
	#

#



