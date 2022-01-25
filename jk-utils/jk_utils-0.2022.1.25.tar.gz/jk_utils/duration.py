







_GREGORIAN_CALENDAR_YEAR_IN_DAYS = 365.2425
_GREGORIAN_CALENDAR_YEAR_IN_SECONDS = 365.2425 * 24*60*60
_GREGORIAN_CALENDAR_AVG_DAYS_PER_MONTH = _GREGORIAN_CALENDAR_YEAR_IN_DAYS / 12
_GREGORIAN_CALENDAR_AVG_SECONDS_PER_MONTH = _GREGORIAN_CALENDAR_YEAR_IN_DAYS * 24*60*60 / 12
_GREGORIAN_CALENDAR_SECONDS_PER_WEEK = 24*60*60*7
_GREGORIAN_CALENDAR_SECONDS_PER_DAY = 24*60*60
_GREGORIAN_CALENDAR_SECONDS_PER_HOUR = 60*60
_GREGORIAN_CALENDAR_SECONDS_PER_MINUTE = 60










#
# Splits the specified number of seconds into years, months, weeks, days, hours, minutes and seconds.
#
# As long as the time remains below the amount of one month all return values can be calculated absolutely accurately. In that case
# <c>(0, 0, weeks, days, hours, minutes, seconds)</c> is returned.
#
# If the time is greater or equal to the duration of one month this can no longer be calculated accurately, as the length of the months differ. In that case 
# <c>(years, months, weeks, -1, -1, -1, -1)</c> is returned.
# As this function is intended to calculate values for displaying time durations, a better accuracy doesn't make any sense anyway.
#
def secondsToYMWDHMS(fSeconds:float) -> tuple:
	assert isinstance(fSeconds, (float,int))
	assert fSeconds >= 0

	if fSeconds >= _GREGORIAN_CALENDAR_YEAR_IN_SECONDS:
		years = int(fSeconds / _GREGORIAN_CALENDAR_YEAR_IN_SECONDS)
		fSeconds = fSeconds - years * _GREGORIAN_CALENDAR_YEAR_IN_SECONDS
	else:
		years = 0

	if fSeconds >= _GREGORIAN_CALENDAR_AVG_SECONDS_PER_MONTH:
		months = int(fSeconds / _GREGORIAN_CALENDAR_AVG_SECONDS_PER_MONTH)
		fSeconds = fSeconds - months * _GREGORIAN_CALENDAR_AVG_SECONDS_PER_MONTH
	else:
		months = 0

	if fSeconds >= _GREGORIAN_CALENDAR_SECONDS_PER_WEEK:
		weeks = int(fSeconds / _GREGORIAN_CALENDAR_SECONDS_PER_WEEK)
		fSeconds = fSeconds - weeks * _GREGORIAN_CALENDAR_SECONDS_PER_WEEK
	else:
		weeks = 0

	if (years > 0) or (months > 0):
		return (years, months, weeks, -1, -1, -1, -1)

	if fSeconds >= _GREGORIAN_CALENDAR_SECONDS_PER_DAY:
		days = int(fSeconds / _GREGORIAN_CALENDAR_SECONDS_PER_DAY)
		fSeconds = fSeconds - days * _GREGORIAN_CALENDAR_SECONDS_PER_DAY
	else:
		days = 0

	if fSeconds >= _GREGORIAN_CALENDAR_SECONDS_PER_HOUR:
		hours = int(fSeconds / _GREGORIAN_CALENDAR_SECONDS_PER_HOUR)
		fSeconds = fSeconds - hours * _GREGORIAN_CALENDAR_SECONDS_PER_HOUR
	else:
		hours = 0

	if fSeconds >= _GREGORIAN_CALENDAR_SECONDS_PER_MINUTE:
		minutes = int(fSeconds / _GREGORIAN_CALENDAR_SECONDS_PER_MINUTE)
		fSeconds = fSeconds - minutes * _GREGORIAN_CALENDAR_SECONDS_PER_MINUTE
	else:
		minutes = 0

	seconds = int(fSeconds)

	return (years, months, weeks, days, hours, minutes, seconds)
#




_NAMES_EN = {
	"second": ( "1 second", "{} seconds" ),
	"minute": ( "1 minute", "{} minutes" ),
	"hour": ( "1 hour", "{} hours" ),
	"day": ( "1 day", "{} days" ),
	"week": ( "1 week", "{} weeks" ),
	"month": ( "1 month", "{} months" ),
	"year": ( "1 year", "{} years" ),
}



def secondsToHRStr(fSeconds:float) -> str:
	y, m, w, d, h, m2, s = secondsToYMWDHMS(fSeconds)

	bNoWeeks = False
	bNoHours = False
	bNoMinutes = False
	bNoSeconds = False

	if y <= 0:
		sYears = ""
	else:
		_names = _NAMES_EN["year"]
		sYears = _names[0] if y == 1 else _names[1].format(y)
		bNoWeeks = True
		bNoHours = True
		bNoMinutes = True
		bNoSeconds = True

	if m <= 0:
		sMonths = ""
	else:
		_names = _NAMES_EN["month"]
		sMonths = _names[0] if m == 1 else _names[1].format(m)
		bNoHours = True
		bNoMinutes = True
		bNoSeconds = True

	if bNoWeeks or (w <= 0):
		sWeeks = ""
	else:
		_names = _NAMES_EN["week"]
		sWeeks = _names[0] if w == 1 else _names[1].format(w)
		bNoHours = True
		bNoMinutes = True
		bNoSeconds = True

	if d <= 0:
		sDays = ""
	else:
		_names = _NAMES_EN["day"]
		sDays = _names[0] if d == 1 else _names[1].format(d)
		bNoMinutes = True
		bNoSeconds = True

	if bNoHours or (h <= 0):
		sHours = ""
	else:
		_names = _NAMES_EN["hour"]
		sHours = _names[0] if h == 1 else _names[1].format(h)
		bNoSeconds = True

	if bNoMinutes or (m2 <= 0):
		sMinutes = ""
	else:
		_names = _NAMES_EN["minute"]
		sMinutes = _names[0] if m2 == 1 else _names[1].format(m2)

	if bNoSeconds or (s <= 0):
		sSeconds = ""
	else:
		_names = _NAMES_EN["second"]
		sSeconds = _names[0] if s == 1 else _names[1].format(s)

	col = [
		sYears,
		sMonths,
		sWeeks,
		sDays,
		sHours,
		sMinutes,
		sSeconds,
	]
	ret = ", ".join([ item for item in col if item ])
	if ret:
		return ret
	else:
		return "now"
#





