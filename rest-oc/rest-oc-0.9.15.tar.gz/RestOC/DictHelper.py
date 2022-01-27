# coding=utf8
""" Dictionary Helper Module

Several useful helper methods for use with dicts
"""

__author__ = "Chris Nasr"
__copyright__ = "OuroborosCoding"
__version__ = "1.0.0"
__email__ = "chris@ouroboroscoding.com"
__created__ = "2018-11-11"

# Python imports
import sys

def clone(src):
	"""Clone

	Goes through the dict and any child dicts copying the values so that we
	don't have any references

	Arguments:
		src (dict): The source dict

	Returns:
		dict
	"""

	# Check the argument
	if not isinstance(src, dict):
		raise ValueError('%s is not a valid value for src argument of %s' % (str(src), sys._getframe().f_code.co_name))

	# Initialise the new dict
	dRet = {}

	# Get each key of the source dict
	for k in src:

		# If the key points to another dict
		if isinstance(src[k], dict):

			# Call clone on it
			dRet[k] = clone(src[k])

		# Else if the key points to a list
		elif isinstance(src[k], list):

			# Use list magic to copy it
			dRet[k] = src[k][:]

		# Else it's a standard variable
		else:
			dRet[k] = src[k]

	# Return the new dict
	return dRet

def combine(first, second):
	"""Combine

	Generates a new dict by combining the two passed, values in second will
	overwrite values in first

	Arguments:
		first (dict): The dict to be changed/overwritten
		second (dict): The dict that will do the overwriting

	Returns:
		dict
	"""

	# Make sure both arguments are actual dicts
	if not isinstance(first, dict):
		raise ValueError('%s is not a valid value for first of %s' % (str(first), sys._getframe().f_code.co_name))
	if not isinstance(second, dict):
		raise ValueError('%s is not a valid value for second of %s' % (str(second), sys._getframe().f_code.co_name))

	# Copy the first dict
	dRet = clone(first)

	# Get each key of the second dict
	for m in second:

		# If the value is another dict and it exists in first as well
		if isinstance(second[m], dict) and m in dRet and isinstance(dRet[m], dict):

			# Call combine
			dRet[m] = combine(dRet[m], second[m])

		# else we overwrite the value as is
		else:
			dRet[m] = second[m]

	# Return the new dict
	return dRet

# Evaluate function
def eval(src, contains):
	"""Eval(uate)

	Goes through a dict looking for keys from contains

	Arguments:
		src (dict): The dict we are evaluating
		contains (list): A list of values to check for, if the value is a dict
			rather than a string, epects keys to be keys pointing to further
			lists of keys

	Return:
		A list of errors, or None
	"""

	# Initialise the list of errors
	lErrs = []

	# Go through each contains value
	for s in contains:

		# If the value is a string
		if isinstance(s, str):

			# If value does not exist in the source
			if s not in src or (isinstance(src[s], str) and not src[s]):
				lErrs.append(s)

		# Else, if we got a dict
		elif isinstance(s, dict):

			# Go through the key/value pairs in the dict
			for k,v in s.items():

				# If the key doesn't exist in the source or has no value
				if k not in src or not src[k]:
					lErrs.append(k)

				# Else, check the children
				else:

					# Call the eval on the child dict
					lChildErrs = eval(src[k], v)

					# Add errors to the list
					if lChildErrs:
						for sErr in lChildErrs:
							lErrs.append(k + '.' + sErr)

		# We got an unknown type of key
		else:
			lErrs.append(str(s))

	# If there's any errors
	if lErrs:
		raise ValueError(*lErrs)

def keysToInts(src):
	"""Keys To Ints

	Recursively goes through a dictionary and converts all keys that are
	numeric but stored as strings to integers. Returns a new dict and doesn't
	alter the original.

	PLEASE NOTE: this method is not useful for classes, or anything complex, it
	is meant primarily for converting JSON objects which don't allow ints as
	keys. Passing a set, tuple, or iterable class will not result in the
	expected result

	Arguments:
		src (dict|list): The dict we are modifying, accepts lists in order to
							handle recursive following the data

	Returns:
		dict|list
	"""

	# If we got a dict
	if isinstance(src, dict):

		# Init the return value to an empty dict
		mRet = {}

		# Go through the each key of the source
		for k in src:

			# Is the value numeric?
			try: mK = int(k)
			except ValueError: mK = k

			# If we got a dict or list, recurse it
			if isinstance(src[k], (dict,list)):
				mRet[mK] = keysToInts(src[k])

			# Else, store as is
			else:
				mRet[mK] = src[k]

	# Else, if we got a list
	elif isinstance(src, list):

		# Init the result value to a list
		mRet = []

		# Go through each item in the list
		for i in range(len(src)):

			# If we got a dict or list, recurse it
			if isinstance(src[i], (dict,list)):
				mRet.append(keysToInts(src[i]))

			# Else, store as is
			else:
				mRet.append(src[k])

	# Else, raise an error
	else:
		raise ValueError('src of %s must be a dict or list, received %s' % (sys._getframe().f_code.co_name, str(type(src))))

	# Return the new data
	return mRet
