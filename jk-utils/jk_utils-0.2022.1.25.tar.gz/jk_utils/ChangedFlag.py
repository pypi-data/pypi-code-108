





class ChangedFlag(object):

	def __init__(self, value):
		assert isinstance(value, bool)
		self.__value = value
	#

	@property
	def value(self):
		return self.__value
	#

	@property
	def isChanged(self):
		return self.__value
	#

	def setChanged(self, value):
		assert isinstance(value, bool)
		self.__value = value
	#

	def __str__(self):
		if self.__value:
			return "changed"
		else:
			return "unchanged"
	#

	def __repr__(self):
		return self.__str__()
	#

	def __eq__(self, other):
		if isinstance(other, ChangedFlag):
			return other.__value == self.__value
		else:
			return False
	#

	def __ne__(self, other):
		if isinstance(other, ChangedFlag):
			return other.__value != self.__value
		else:
			return True
	#








