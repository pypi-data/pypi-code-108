

import typing
import datetime

import jk_typing






_EPOCH = datetime.datetime.utcfromtimestamp(0)

def _dateTimeToSecondsSinceEpoch(dt:datetime.datetime) -> float:
	assert isinstance(dt, datetime.datetime)
	return (dt - _EPOCH).total_seconds()
#

def _secondsSinceEpocheToDateTime(t:float) -> datetime.datetime:
	assert isinstance(t, float)
	assert t >= 0
	return datetime.datetime.utcfromtimestamp(t)
#







class TimeStamp(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	@jk_typing.checkFunctionSignature()
	def __init__(self, value):
		if isinstance(value, (int,float)):
			self.__t = value
		elif isinstance(value, datetime.datetime):
			self.__t = _dateTimeToSecondsSinceEpoch(value)
		else:
			raise Exception()
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def secondsSinceEpoch(self) -> float:
		return self.__t
	#

	@property
	def dateTime(self) -> datetime.datetime:
		return _secondsSinceEpocheToDateTime(self.__t)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __repr__(self):
		return "TimeStamp<({})".format(self.dateTime)
	#

	def __str__(self):
		return "TimeStamp<({})".format(self.dateTime)
	#

	#
	# Use this method to retrieve formatted output of the data.
	#
	def toStr(self) -> str:
		return "{}".format(self.dateTime)
	#

	def toDateTime(self) -> datetime.datetime:
		return _secondsSinceEpocheToDateTime(self.__t)
	#

	def __float__(self):
		return self.__t
	#

	def __int__(self):
		return int(self.__t)
	#

	def __sub__(self, other):
		if isinstance(other, TimeStamp):
			return self.__t - other.__t
		elif isinstance(other, (int,float)):
			return TimeStamp(self.__t - other)
		else:
			raise TypeError(repr(other))
	#

	def __add__(self, other):
		if isinstance(other, (int,float)):
			return TimeStamp(self.__t + other)
		else:
			raise TypeError(repr(other))
	#

	def __gt__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		return self.__t > tOther
	#

	def __ge__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		return self.__t >= tOther
	#

	def __lt__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		return self.__t < tOther
	#

	def __le__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		return self.__t <= tOther
	#

	def __eq__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		fDiff = abs(self.__t - tOther)
		return fDiff < 0.0000000001
	#

	def __ne__(self, other):
		tOther = None
		if isinstance(other, (int,float)):
			tOther = other
		elif isinstance(other, datetime.datetime):
			tOther = _dateTimeToSecondsSinceEpoch(other)
		elif isinstance(other, TimeStamp):
			tOther = other.__t
		else:
			raise TypeError(repr(other))

		fDiff = abs(self.__t - tOther)
		return fDiff >= 0.0000000001
	#

	################################################################################################################################
	## Public Static Methods
	################################################################################################################################

	@staticmethod
	def parse(v:typing.Union[int,float]):
		assert isinstance(v, (int,float))
		return TimeStamp(v)
	#

	@staticmethod
	def now():
		return TimeStamp(datetime.datetime.utcnow())
	#

#


