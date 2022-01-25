

import typing
import time







#
# This class is a proxy for a value. The data will be cached for the number of seconds specified. If data is outdated the data is generated again (and stored again for the number
# of seconds specified.)
#
class VolatileValue(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, valueProviderCallback, keepSeconds:int, args:typing.Union[list,tuple] = None, kwargs:dict = None):
		assert callable(valueProviderCallback)
		assert isinstance(keepSeconds, int)
		if args is not None:
			assert isinstance(args, (list,tuple))
		if kwargs is not None:
			assert isinstance(kwargs, dict)

		# ----

		self.__args = args if args else []
		self.__kwargs = kwargs if kwargs else {}
		self.__keepSeconds = keepSeconds
		self.__valueProviderCallback = valueProviderCallback
		self.__value = None
		self.__t = 0
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def value(self):
		t = time.time()
		if (t - self.__t > self.__keepSeconds):
			self.__value = self.__valueProviderCallback(*self.__args, **self.__kwargs)
			# self.__t = t
		return self.__value
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def invalidate(self):
		self.__value = None
		self.__t = 0
	#

#














