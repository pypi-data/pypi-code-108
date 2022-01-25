


import datetime
import re





#
# This class represents a date.
#
class D(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self):
		self._dt = None
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# The time stamp in seconds
	#
	@property
	def ts(self) -> int:
		return int(self._dt.timestamp())
	#

	#
	# The time stamp in nanoseconds.
	#
	def tsNano(self) -> int:
		return int(self._dt.timestamp() * 1000000)
	#

	@property
	def year(self) -> int:
		return self._dt.year
	#

	#
	# The month of this year, starting with one.
	#
	@property
	def month(self) -> int:
		return self._dt.month
	#

	#
	# The month of this year, starting with zero.
	#
	@property
	def month0(self) -> int:
		return self._dt.month - 1
	#

	#
	# The day of this month, starting with one.
	#
	@property
	def day(self) -> int:
		return self._dt.day
	#

	#
	# The day of this month, starting with zero.
	#
	@property
	def day0(self) -> int:
		return self._dt.day - 1
	#

	#
	# The week day: Monday = 1, Tuesday = 2, ..., Sunday = 7
	#
	@property
	def dayOfWeek(self) -> int:
		return self._dt.weekday() + 1
	#

	#
	# The week day: Monday = 0, Tuesday = 1, ..., Sunday = 6
	#
	@property
	def dayOfWeek0(self) -> int:
		return self._dt.weekday()
	#

	#
	# The week day: Monday = 1, Tuesday = 2, ..., Sunday = 7
	#
	@property
	def weekday(self) -> int:
		return self._dt.weekday() + 1
	#

	#
	# The week day: Monday = 0, Tuesday = 1, ..., Sunday = 6
	#
	@property
	def weekday0(self) -> int:
		return self._dt.weekday() + 1
	#

	#
	# This date in 8 digit year-month-day representaion.
	#
	@property
	def yearMonthDay(self) -> int:
		return self._dt.year * 10000 + self._dt.month * 100 + self._dt.day
	#

	#
	# This date in 6 digit year-month representaion.
	#
	@property
	def yearMonth(self) -> int:
		return self._dt.year * 100 + self._dt.month
	#

	"""
	#
	# Calculates the week number (using ISO week number algorithm, where Jan 1st is in week 1)
	#
	@property
	def weekNo(self):
		d = datetime.datetime(self.year, 1, 1)

		# the week day of the first day in this year:
		# 1 = monday, 2 = tuesday, ..., 7 = sunday
		firstJanWeekDay = ((d.weekday() + 1) + 7) % 7
		correction = 0 if firstJanWeekDay == 0 else (7 - (- firstJanWeekDay + 1))
		td = self._dt - d
		return (td.days + correction) // 7
	#
	"""

	#
	# Official week number (where the week, that has the majority of days in this year, is week 1)
	#
	@property
	def weekNo(self):
		return self._dt.isocalendar()[1]
	#

	################################################################################################################################
	## Special Methods
	################################################################################################################################

	def __str__(self):
		return "{:04d}-{:02d}-{:02d}".format(self._dt.year, self._dt.month, self._dt.day)
	#

	def __repr__(self):
		return "{:04d}-{:02d}-{:02d}".format(self._dt.year, self._dt.month, self._dt.day)
	#

	def __hash__(self):
		return (self._dt.year * 10000 + self._dt.month * 100 + self._dt.day).__hash__()
	#

	################################################################################################################################
	## Operator Methods
	################################################################################################################################

	def __eq__(self, other):
		if isinstance(other, D):
			return self._dt == other._dt
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, D):
			return self._dt != other._dt
		else:
			return True
	#

	def __ge__(self, other):
		assert isinstance(other, D)
		return self._dt >= other._dt
	#

	def __gt__(self, other):
		assert isinstance(other, D)
		return self._dt > other._dt
	#

	def __le__(self, other):
		assert isinstance(other, D)
		return self._dt <= other._dt
	#

	def __lt__(self, other):
		assert isinstance(other, D)
		return self._dt < other._dt
	#

	def __add__(self, other):
		if isinstance(other, int):
			return D.createFrom(dt=int(self._dt.timestamp() + 24*60*60*other))
		else:
			raise Exception(str(type(other)))
	#

	def __iadd__(self, other):
		if isinstance(other, int):
			self._dt = datetime.datetime.fromtimestamp(self._dt.timestamp() + 24*60*60*other)
			return self
		else:
			raise Exception(str(type(other)))
	#

	def __sub__(self, other):
		if isinstance(other, int):
			return D.createFrom(dt=int(self._dt.timestamp() - 24*60*60*other))
		elif isinstance(other, D):
			delta = self._dt.timestamp() - other._dt.timestamp()
			return int(delta / (24*60*60))
		else:
			raise Exception(str(type(other)))
	#

	def __isub__(self, other):
		if isinstance(other, int):
			self._dt = datetime.datetime.fromtimestamp(self._dt.timestamp() - 24*60*60*other)
			return self
		else:
			raise Exception(str(type(other)))
	#

	def __int__(self):
		return int(self._dt.timestamp())
	#

	def __float__(self):
		return self._dt.timestamp()
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def toISOStr(self):
		return "{:04d}-{:02d}-{:02d}".format(self._dt.year, self._dt.month, self._dt.day)
	#

	def toEUStr(self):
		return "{:02d}.{:02d}.{:04d}".format(self._dt.day, self._dt.month, self._dt.year)
	#

	def toJSON(self) -> dict:
		return {
			"year": self._dt.year,
			"month": self._dt.month,
			"day": self._dt.day,
			"ts": int(self._dt.timestamp()),
			"yearMonth": self.yearMonth,
			"yearMonthDay": self.yearMonthDay,
			"isostr": str(self),
		}
	#

	#
	# Creates a D object representing the first of January of this year
	#
	# @return		D		A new date object
	#
	def startOfYear(self):
		ret = D()
		ret._dt = datetime.datetime(self.year, 1, 1)
		return ret
	#

	#
	# Creates a D object representing the 31st of December of this year
	#
	# @return		D		A new date object
	#
	def endOfYear(self):
		ret = D()
		ret._dt = datetime.datetime(self.year, 12, 31)
		return ret
	#

	#
	# @return		D		A new date object
	#
	def startOfMonth(self):
		ret = D()
		ret._dt = datetime.datetime(self.year, self.month, 1)
		return ret
	#

	#
	# @return		D		A new date object
	#
	def endOfMonth(self):
		y = self.year
		m = self.month + 1
		if m > 12:
			y += 1
			m -= 12
		dt = datetime.datetime(y, m, 1)
		dt = dt - datetime.timedelta(days=1)

		ret = D()
		ret._dt = dt
		return ret
	#

	#
	# @return		D		A new date object
	#
	def nextYear(self):
		ret = D()
		ret._dt = datetime.datetime(self.year + 1, self.month, self.day)
		return ret
	#

	#
	# @return		D		A new date object
	#
	def previousYear(self):
		if self.year <= 1:
			raise Exception()
		ret = D()
		ret._dt = datetime.datetime(self.year - 1, self.month, self.day)
		return ret
	#

	#
	# @return		D		A new date object
	#
	def nextMonth(self):
		y = self.year
		m = self.month
		d = self.day

		if m == 12:
			m = 1
			y += 1
		else:
			m += 1

		ret = D()
		while True:
			try:
				ret._dt = datetime.datetime(y, m, d)
				break
			except ValueError as ee:
				d -= 1
		return ret
	#

	#
	# @return		D		A new date object
	#
	def previousMonth(self):
		y = self.year
		m = self.month
		d = self.day

		if m == 1:
			m = 12
			y -= 1
		else:
			m -= 1

		ret = D()
		while True:
			try:
				ret._dt = datetime.datetime(y, m, d)
				break
			except ValueError as ee:
				d -= 1
		return ret
	#

	#
	# @return		D		A new date object
	#
	def startOfWeek(self):
		wd = self._dt.weekday()
		dt = self._dt.timestamp() - 24*60*60*wd
		d = D()
		d._dt = datetime.datetime.fromtimestamp(dt)
		return d
	#

	#
	# @return		D		A new date object
	#
	def endOfWeek(self):
		wd = self._dt.weekday()
		dt = self._dt.timestamp() - 24*60*60*wd + 24*60*60*6
		d = D()
		d._dt = datetime.datetime.fromtimestamp(dt)
		return d
	#

	#
	# @return		D		A new date object
	#
	def nextWeek(self):
		wd = self._dt.weekday()
		dt = self._dt.timestamp() - 24*60*60*wd
		d = D()
		d._dt = datetime.datetime.fromtimestamp(dt + 7 *24*60*60)
		return d
	#

	#
	# @return		D		A new date object
	#
	def previousWeek(self):
		wd = self._dt.weekday()
		dt = self._dt.timestamp() - 24*60*60*wd
		d = D()
		d._dt = datetime.datetime.fromtimestamp(dt - 7 *24*60*60)
		return d
	#

	#
	# @return		D		A new date object
	#
	def nextDay(self):
		d = D()
		d._dt = datetime.datetime.fromtimestamp(self._dt.timestamp() + 24*60*60)
		return d
	#

	#
	# @return		D		A new date object
	#
	def previousDay(self):
		d = D()
		d._dt = datetime.datetime.fromtimestamp(self._dt.timestamp() - 24*60*60)
		return d
	#

	#
	# @return		D		A new date object
	#
	def addMonths(self, m:int):
		assert isinstance(m, int)

		yy = self.year
		mm = self.month
		dd = self.day

		if m > 0:
			mm += m % 12
			yy += m // 12
		else:
			m = -m
			mm -= m % 12
			yy -= m // 12
			if mm < 1:
				yy -= 1
				mm += 12
		
		return D.createFrom(yearMonthDayTuple=(yy, mm, dd))
	#

	#
	# @return		D		A new date object
	#
	def subtractMonths(self, m:int):
		assert isinstance(m, int)

		return self.addMonths(-m)
	#

	#
	# @return		D		A new date object
	#
	def addYears(self, y:int):
		assert isinstance(y, int)

		yy = self.year + y
		mm = self.month
		dd = self.day

		return D.createFrom(yearMonthDayTuple=(yy, mm, dd))
	#

	#
	# @return		D		A new date object
	#
	def subtractYears(self, y:int):
		assert isinstance(y, int)

		return self.addYears(-y)
	#

	#
	# @return		D		A new date object
	#
	def clone(self):
		ret = D()
		ret._dt = self._dt
		return ret
	#

	#
	# @return	D[]		Returns a list of date objects containing all seven days of this week.
	#
	def generateWeekDates(self) -> list:
		d = self.startOfWeek()
		ret = [ d ]
		for i in range(0, 6):
			d = d.nextDay()
			ret.append(d)
		return ret
	#

	################################################################################################################################
	## Static Methods
	################################################################################################################################

	#
	# Returns a date object of today.
	# This is the same as "today()`.
	#
	@staticmethod
	def now():
		ret = D()
		dt = datetime.datetime.now()
		y = dt.year
		m = dt.month
		d = dt.day
		ret._dt = datetime.datetime(y, m, d)
		return ret
	#

	#
	# Returns a date object of today.
	# This is the same as "now()`.
	#
	@staticmethod
	def today():
		ret = D()
		dt = datetime.datetime.now()
		y = dt.year
		m = dt.month
		d = dt.day
		ret._dt = datetime.datetime(y, m, d)
		return ret
	#

	@staticmethod
	def tryParseFromStr(s:str):
		if isinstance(s, str):
			s = s.strip()
			for dt, year, month, day in D.__tryParse(s):
				if dt is None:
					if year is None:
						d0 = D.now()
						year = d0._dt.year
						try:
							d1 = D.createFrom(yearMonthDayTuple=(year, month, day))
							if d1 < d0:
								d1 = D.createFrom(yearMonthDayTuple=(year + 1, month, day))
							return d1
						except:
							pass
					else:
						try:
							return D.createFrom(yearMonthDayTuple=(year, month, day))
						except:
							pass
				else:
					try:
						return D.createFrom(dt=dt)
					except:
						pass
		return None
	#

	@staticmethod
	def parseFromStr(s:str):
		d = D.tryParseFromStr(s)
		if d is None:
			raise Exception("Failed to parse: " + repr(s))
		return d
	#

	@staticmethod
	def __tryParse(s:str):
		for patternType, pattern in [
			("ymd", r"(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)"),
			("ymd", r"(?P<day>\d\d?)\.(?P<month>\d\d?)\.(?P<year>\d\d\d\d)"),
			("ymd", r"(?P<month>\d\d?)/(?P<day>\d\d?)/(?P<year>\d\d\d\d)"),
			("md", r"(?P<day>\d\d?)\.(?P<month>\d\d?)\."),
			("ts", r"(?P<ts>-?\d+)"),
		]:
			m = re.match("^" + pattern + "$", s)
			if m:
				if patternType == "ts":
					try:
						yield (int(s), None, None, None)
					except:
						pass
				elif patternType == "ymd":
					year = int(m.group("year"))
					month = int(m.group("month"))
					day = int(m.group("day"))
					if (1 <= month <= 12) and (1 <= day <= 31) and (100 <= year <= 2999):
						yield (None, year, month, day)
				elif patternType == "md":
					month = int(m.group("month"))
					day = int(m.group("day"))
					if (1 <= month <= 12) and (1 <= day <= 31):
						yield (None, None, month, day)
				else:
					raise Exception()
	#

	@staticmethod
	def createFrom(something = None, dt:int = None, yearMonthDay:int = None, yearMonth:int = None, yearMonthDayTuple:list = None):
		ret = D()

		if dt is not None:
			if isinstance(dt, datetime.datetime):
				ret._dt = D.__createFrom_timeStamp(dt)
			elif isinstance(dt, (int, float)):
				ret._dt = D.__createFrom_timeStamp(dt)
			else:
				raise Exception()
		elif yearMonthDay is not None:
			ret._dt = D.__createFrom_yearMonthDay(yearMonthDay)
		elif yearMonth is not None:
			ret._dt = D.__createFrom_yearMonth(yearMonth)
		elif yearMonthDayTuple is not None:
			ret._dt = D.__createFrom_yearMonthDayTuple(yearMonthDayTuple)
		elif something is not None:
			if isinstance(something, datetime.datetime):
				ret._dt = something
			elif isinstance(something, float):
				ret._dt = D.__createFrom_timeStamp(something)
			elif isinstance(something, int):
				if 10000000 < something < 29999999:
					ret._dt = D.__createFrom_yearMonthDay(something)
				elif 100000 < something < 299999:
					ret._dt = D.__createFrom_yearMonth(something)
				elif something > 999999999:
					ret._dt = D.__createFrom_timeStamp(something)
				else:
					raise Exception()
			elif isinstance(something, str):
				ret = D.parseFromStr(something)
			elif isinstance(something, (tuple, list)):
				ret._dt = D.__createFrom_yearMonthDayTuple(something)
			else:
				raise Exception()
		else:
			raise Exception()

		return ret
	#

	@staticmethod
	def __createFrom_timeStamp(timeStamp:float) -> datetime.datetime:
		dt = datetime.datetime.fromtimestamp(timeStamp)
		year = dt.year
		month = dt.month
		day = dt.day
		return datetime.datetime(year, month, day)
	#

	@staticmethod
	def __createFrom_yearMonth(yearMonth:int) -> datetime.datetime:
		year = yearMonth // 100
		month = yearMonth % 100
		day = 1
		return datetime.datetime(year, month, day)
	#

	@staticmethod
	def __createFrom_yearMonthDay(yearMonthDay:int) -> datetime.datetime:
		year = yearMonthDay // 10000
		month = (yearMonthDay // 100) % 100
		day = yearMonthDay % 100
		return datetime.datetime(year, month, day)
	#

	@staticmethod
	def __createFrom_yearMonthDayTuple(yearMonthDayTuple) -> datetime.datetime:
		assert isinstance(yearMonthDayTuple, (list, tuple))
		assert len(yearMonthDayTuple) == 3
		assert isinstance(yearMonthDayTuple[0], int)
		assert isinstance(yearMonthDayTuple[1], int)
		assert isinstance(yearMonthDayTuple[2], int)
		return datetime.datetime(yearMonthDayTuple[0], yearMonthDayTuple[1], yearMonthDayTuple[2])
	#

#















