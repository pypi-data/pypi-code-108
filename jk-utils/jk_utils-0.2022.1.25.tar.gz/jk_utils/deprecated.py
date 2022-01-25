


import sys
import warnings



__WARNING_COLOR = "\033[93m"
__RESET_COLOR = "\033[0m"
__REMEMBER_DEPRECATIONS = {}



#
# This is a decorator which can be used to mark functions as deprecated.
# It will result in a warning being emitted when the function is used.
#
def deprecated(func):

	__REMEMBER_DEPRECATIONS[func] = False

	def new_func(*args, **kwargs):
		if not __REMEMBER_DEPRECATIONS[func]:
			warnings.simplefilter("always", DeprecationWarning)  # turn off filter
			errMsg = "Call to deprecated function '{}()'.".format(func.__name__)
			if sys.stdin.isatty():
				errMsg = __WARNING_COLOR + errMsg + __RESET_COLOR
			warnings.warn(
				errMsg,
				category=DeprecationWarning,
				stacklevel=2)
			warnings.simplefilter("default", DeprecationWarning)		# reset filter
			__REMEMBER_DEPRECATIONS[func] = True

		return func(*args, **kwargs)
	#

	return new_func
#









