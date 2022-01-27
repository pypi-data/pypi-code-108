# coding=utf8
""" Date & Time Helper Module

Several useful helper methods for use with dates and times
"""

# Compatibility
from past.builtins import basestring

__author__ = "Chris Nasr"
__copyright__ = "OuroborosCoding"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2021-05-01"

# Python imports
from math import floor

# Pip imports
import arrow

def _toArrow(val):
	"""To Arrow

	Converts a value to an Arrow instance for easier use

	Arguments:
		val (mixed): An value that can hopefully be turned into some sort of
						date/time

	Returns:
		arrow.arrow.Arrow
	"""

	# If we got a timestamp
	if isinstance(val, int):
		return arrow.get(val);

	# If we got a string
	if isinstance(val, basestring):

		# If it's only ten characters, add the time and timezone
		if len(val) == 10:
			return arrow.get('%sT00:00:00+00:00' % val)

		# If it's 19 characters, replace any space with T and add the timezone
		if len(val) == 19:
			return arrow.get('%+00:00' % val.replace(' ', 'T'))

		# If it's 25 characters, assume it's good
		if len(val) == 25:
			return arrow.get(val);

		# Raise an exception
		raise ValueError('Invalid date string', val)

	# If it's already an arrow instance
	if isinstance(val, arrow.arrow.Arrow):
		return val

	# Raise an exception
	raise ValueError('Invalid date/time', val)

def age(dob):
	"""Age

	Returns the current age of someone based on today's date and their DOB.
	This method is not %100 accurate, but it's good enough for 99% of cases

	Arguments:
		dob (Arrow|uint|str): The date of birth of the person

	Returns:
		uint
	"""

	# Make sure we have an arrow instance
	oDOB = _toArrow(dob)

	# Get the delta from today
	oDelta = arrow.get() - oDOB

	# Return the age
	return floor(oDelta.days / 365.25)

def date(d):
	"""Date

	Returns a string in YYYY-MM-DD format from a timestamp, date string, or
	arrow instance

	Arguments:
		d (Arrow|uint|str): The date to format

	Returns:
		str
	"""

	# Make sure we have an arrow instance
	oD = _toArrow(d)

	# Return the date string
	return oD.format('YYYY-MM-DD')

def dateInc(days=1, from_=None):
	"""Date Increment

	Returns a date incremented by the given days. Use negative to decrement.

	Arguments:
		days (int): The number of days to increment (or decrement) by
		from_ (mixed): Optional, the date to increment from, else today

	Returns:
		arrow.arrow.Arrow
	"""

	# If we got a from
	oDate = from_ and _toArrow(from_) or arrow.get();

	# Increment the date and return it
	return oDate.shift(days=days)

def datetime(d):
	"""Date Time

	Returns a string in YYYY-MM-DD HH:mm:ss format from a timestamp, date
	string, or arrow instance

	Arguments:
		d (Arrow|uint|str): The date to format

	Returns:
		str
	"""

	# Make sure we have an arrow instance
	oD = _toArrow(d)

	# Return the date/time string
	return oD.format('YYYY-MM-DD HH:mm:ss')

def timeElapsed(seconds):
	"""Time Elapsed

	Returns seconds in a human readable format

	Arguments:
		seconds (uint): The seconds to convert to ((HH:)mm:)ss

	Returns:
		str
	"""

	# Get the hours and remaining seconds
	h, r = divmod(seconds, 3600)

	# Get the minutes and seconds
	m, s = divmod(r, 60)

	# Init the list we'll turn into time
	lTime = None

	# If we have hours
	if h:
		lTime = [
			str(h),
			m < 10 and '0%d' %m or str(m),
			s < 10 and '0%d' %s or str(s)
		]

	# Else, if we have minutes
	elif m:
		lTime = [
			str(m),
			s < 10 and '0%d' % s or str(s)
		]

	# Else, we only have seconds
	else:
		lTime = [
			str(s)
		]

	# Put them all together and return
	return ':'.join(lTime)
