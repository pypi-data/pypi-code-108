

import re
import datetime






#
# This class represents a time value with a 1 minute accuracy.
#
class T1(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self):
		self._hour = 0
		self._minute = 0
		self._absoluteTick = 0
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def hour(self) -> int:
		return self._hour
	#

	@property
	def minute(self) -> int:
		return self._minute
	#

	@property
	def hourMinute(self) -> int:
		return self._hour * 100 + self._minute
	#

	@property
	def absoluteTick(self) -> int:
		return self._absoluteTick
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def clone(self):
		ret = T1()
		ret._hour = self._hour
		ret._minute = self._minute
		ret._absoluteTick = self._absoluteTick
		return ret
	#

	################################################################################################################################
	## Special Methods
	################################################################################################################################

	def __str__(self):
		return "{:02d}:{:02d}".format(self._hour, self._minute)
	#

	def __repr__(self):
		return "{:02d}:{:02d}".format(self._hour, self._minute)
	#

	def __eq__(self, other):
		if isinstance(other, T1):
			return self._absoluteTick == other._absoluteTick
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, T1):
			return self._absoluteTick != other._absoluteTick
		else:
			return True
	#

	def __ge__(self, other):
		assert isinstance(other, T1)
		return self._absoluteTick >= other._absoluteTick
	#

	def __gt__(self, other):
		assert isinstance(other, T1)
		return self._absoluteTick > other._absoluteTick
	#

	def __le__(self, other):
		assert isinstance(other, T1)
		return self._absoluteTick <= other._absoluteTick
	#

	def __lt__(self, other):
		assert isinstance(other, T1)
		return self._absoluteTick < other._absoluteTick
	#

	def __iadd__(self, other):
		if isinstance(other, int):
			self._absoluteTick += other
		elif isinstance(other, T1):
			self._absoluteTick += other._absoluteTick
		else:
			raise Exception(str(type(other)))
		self._hour = self._absoluteTick // 60
		self._minute = self._absoluteTick % 60
		return self
	#

	def __isub__(self, other):
		if isinstance(other, int):
			self._absoluteTick -= other
		elif isinstance(other, T1):
			self._absoluteTick -= other._absoluteTick
		else:
			raise Exception(str(type(other)))
		self._hour = self._absoluteTick // 60
		self._minute = self._absoluteTick % 60
		return self
	#

	def __add__(self, other):
		if isinstance(other, int):
			return T1.createFromAbsoluteTick(self._absoluteTick + other)
		elif isinstance(other, T1):
			return T1.createFromAbsoluteTick(self._absoluteTick + other._absoluteTick)
		else:
			raise Exception(str(type(other)))
	#

	def __sub__(self, other):
		if isinstance(other, int):
			return T1.createFromAbsoluteTick(self._absoluteTick - other)
		elif isinstance(other, T1):
			return T1.createFromAbsoluteTick(self._absoluteTick - other._absoluteTick)
		else:
			raise Exception(str(type(other)))
	#

	def __int__(self):
		return self._absoluteTick
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	@staticmethod
	def __tryParse(s:str):
		for patternType, pattern in [
			("hms", r"(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)"),
			("hm", r"(?P<hour>\d\d):(?P<minute>\d\d)"),
		]:
			m = re.match("^" + pattern + "$", s)
			if m:
				if patternType == "hms":
					hour = int(m.group("hour"))
					minute = int(m.group("minute"))
					second = int(m.group("second"))
				elif patternType == "hm":
					hour = int(m.group("hour"))
					minute = int(m.group("minute"))
					second = 0
				else:
					raise Exception()
				if (0 <= hour <= 23) and (0 <= minute <= 59) and (0 <= second <= 59):
					yield (hour, minute, second)
	#

	@staticmethod
	def tryParseFromStr(s:str):
		if isinstance(s, str):
			s = s.strip()
			for hour, minute, second in T1.__tryParse(s):
				return T1.createFromTime(hour, minute)
		return None
	#

	@staticmethod
	def createFromTime(hour:int, minute:int):
		assert isinstance(hour, int)
		assert isinstance(minute, int)

		ret = T1()
		ret._hour = hour
		ret._minute = minute
		ret._absoluteTick = ret._hour * 60 + ret._minute
		return ret
	#

	@staticmethod
	def createFromAbsoluteTick(absoluteTick:int):
		assert isinstance(absoluteTick, int)

		ret = T1()
		ret._hour = absoluteTick // 60
		ret._minute = absoluteTick % 60
		ret._absoluteTick = absoluteTick
		return ret
	#

	@staticmethod
	def createFromHourMinutes(hourMinutes:int):
		assert isinstance(hourMinutes, int)

		ret = T1()
		ret._hour = hourMinutes // 100
		ret._minute = hourMinutes % 100
		if (ret._hour < 0) or (ret._hour > 23) or (ret._minute < 0) or (ret._minute > 59):
			raise Exception("Invalid time!")
		ret._absoluteTick = ret._hour * 60 + ret._minute
		return ret
	#

	@staticmethod
	def now():
		dt = datetime.datetime.now()

		ret = T1()
		ret._hour = dt.hour
		ret._minute = dt.minute
		ret._absoluteTick = ret._hour * 60 + ret._minute
		return ret
	#

#






