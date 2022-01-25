

import re
import datetime






#
# This class represents a time value with a 1 minute accuracy.
#
class TApprox(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self):
		self._hour = 0
		self._minute = 0
		self._absoluteTick = 0
		self._isApproximate = False
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def isApproximate(self) -> bool:
		return self._isApproximate
	#

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
		ret = TApprox()
		ret._hour = self._hour
		ret._minute = self._minute
		ret._absoluteTick = self._absoluteTick
		return ret
	#

	################################################################################################################################
	## Special Methods
	################################################################################################################################

	def __str__(self):
		if self._isApproximate:
			return "ca. {:02d}:{:02d}".format(self._hour, self._minute)
		else:
			return "{:02d}:{:02d}".format(self._hour, self._minute)
	#

	def __repr__(self):
		if self._isApproximate:
			return "ca. {:02d}:{:02d}".format(self._hour, self._minute)
		else:
			return "{:02d}:{:02d}".format(self._hour, self._minute)
	#

	def __eq__(self, other):
		if isinstance(other, TApprox):
			return self._absoluteTick == other._absoluteTick
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, TApprox):
			return self._absoluteTick != other._absoluteTick
		else:
			return True
	#

	def __ge__(self, other):
		assert isinstance(other, TApprox)
		return self._absoluteTick >= other._absoluteTick
	#

	def __gt__(self, other):
		assert isinstance(other, TApprox)
		return self._absoluteTick > other._absoluteTick
	#

	def __le__(self, other):
		assert isinstance(other, TApprox)
		return self._absoluteTick <= other._absoluteTick
	#

	def __lt__(self, other):
		assert isinstance(other, TApprox)
		return self._absoluteTick < other._absoluteTick
	#

	def __iadd__(self, other):
		if isinstance(other, int):
			self._absoluteTick += other
		elif isinstance(other, TApprox):
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
		elif isinstance(other, TApprox):
			self._absoluteTick -= other._absoluteTick
		else:
			raise Exception(str(type(other)))
		self._hour = self._absoluteTick // 60
		self._minute = self._absoluteTick % 60
		return self
	#

	def __add__(self, other):
		if isinstance(other, int):
			return TApprox.createFromAbsoluteTick(self._absoluteTick + other)
		elif isinstance(other, TApprox):
			return TApprox.createFromAbsoluteTick(self._absoluteTick + other._absoluteTick)
		else:
			raise Exception(str(type(other)))
	#

	def __sub__(self, other):
		if isinstance(other, int):
			return TApprox.createFromAbsoluteTick(self._absoluteTick - other)
		elif isinstance(other, TApprox):
			return TApprox.createFromAbsoluteTick(self._absoluteTick - other._absoluteTick)
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
		for approx, patternType, pattern in [
			(False, "hms", r"^(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)"),
			(False,  "hm", r"^(?P<hour>\d\d):(?P<minute>\d\d)"),
			(True, "hms", r"^ca\.?\s*(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)"),
			(True,  "hm", r"^ca\.?\s*(?P<hour>\d\d):(?P<minute>\d\d)"),
		]:
			m = re.match("^" + pattern + "$", s)
			if m:
				if patternType == "hms":
					hour = int(m.group("hour"))
					minute = int(m.group("minute"))
					second = int(m.group("second"))
					posR = m.end()
				elif patternType == "hm":
					hour = int(m.group("hour"))
					minute = int(m.group("minute"))
					second = 0
					posR = m.end()
				else:
					raise Exception()
				if (0 <= hour <= 23) and (0 <= minute <= 59) and (0 <= second <= 59):
					yield (approx, hour, minute, second, posR)
	#

	#
	# Tries to parse a text string such as:
	# * "23:59:00"
	# * "23:59"
	# * "ca. 23:59:00"
	# * "ca. 23:59"
	# * "ca.23:59:00"
	# * "ca.23:59"
	# * "ca 23:59:00"
	# * "ca 23:59"
	#
	# @return		TApprox		The parsed date or <c>None</c> if unparsable
	# @return		int			The number of characters parsed (= <c>0</c> if unparsable)
	#
	@staticmethod
	def tryParseFromStr(s:str) -> tuple:
		if isinstance(s, str):
			s = s.strip()
			for approx, hour, minute, second, posR in TApprox.__tryParse(s):
				return TApprox.createFromTime(hour, minute, approx), posR
		return None, 0
	#

	@staticmethod
	def createFromTime(hour:int, minute:int, isApproximate:bool = False):
		assert isinstance(hour, int)
		assert isinstance(minute, int)
		assert isinstance(isApproximate, bool)

		ret = TApprox()
		ret._hour = hour
		ret._minute = minute
		ret._absoluteTick = ret._hour * 60 + ret._minute
		ret._isApproximate = isApproximate
		return ret
	#

	@staticmethod
	def createFromAbsoluteTick(absoluteTick:int, isApproximate:bool = False):
		assert isinstance(absoluteTick, int)

		ret = TApprox()
		ret._hour = absoluteTick // 60
		ret._minute = absoluteTick % 60
		ret._absoluteTick = absoluteTick
		ret._isApproximate = isApproximate
		return ret
	#

	@staticmethod
	def createFromHourMinutes(hourMinutes:int, isApproximate:bool = False):
		assert isinstance(hourMinutes, int)
		assert isinstance(isApproximate, bool)

		ret = TApprox()
		ret._hour = hourMinutes // 100
		ret._minute = hourMinutes % 100
		if (ret._hour < 0) or (ret._hour > 23) or (ret._minute < 0) or (ret._minute > 59):
			raise Exception("Invalid time!")
		ret._absoluteTick = ret._hour * 60 + ret._minute
		ret._isApproximate = isApproximate
		return ret
	#

	@staticmethod
	def now():
		dt = datetime.datetime.now()

		ret = TApprox()
		ret._hour = dt.hour
		ret._minute = dt.minute
		ret._absoluteTick = ret._hour * 60 + ret._minute
		return ret
	#

#






