


#
# This class wraps around a value. It contains not only the value itself but type information as well.
#
class TypedValue(object):

	def __init__(self, dataType, value):
		self.__dataType = dataType
		self.__value = value
	#

	@property
	def value(self):
		return self.__value
	#

	@property
	def dataType(self):
		return self.__dataType
	#

	def __str__(self):
		if isinstance(self.__value, str):
			return "V(" + self.__dataType + ": \"" + self.__value.replace("\"", "\\\"") + "\")"
		else:
			return "V(" + self.__dataType + ": " + str(self.__value) + ")"
	#

	def __repr__(self):
		return self.__str__()
	#

	def __eq__(self, other):
		if isinstance(other, TypedValue):
			return (other.__dataType == self.__dataType) and (other.__value == self.__value)
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, TypedValue):
			return (other.__dataType != self.__dataType) or (other.__value != self.__value)
		else:
			return True
	#

#








