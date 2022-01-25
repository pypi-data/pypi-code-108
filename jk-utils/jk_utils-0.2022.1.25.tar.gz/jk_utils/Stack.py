


#
# This class implements a stack.
#
# @TODO		Some optimizations might be needed.
#
class Stack(object):

	class _Mark(object):

		def __init__(self, stack, pos):
			self.__stack = stack
			self.__pos = pos
		#

		def resetToMark(self):
			self.__stack._data = self.__stack._data[0:self.__pos]
		#

	#

	def __init__(self):
		self._data = []
	#

	def __iter__(self):
		for v in self._data:
			yield v
	#

	def __len__(self):
		return len(self._data)
	#

	def __str__(self):
		ret = "Stack["
		bAddComma = False
		for item in self._data:
			if bAddComma:
				ret += ", "
			else:
				bAddComma = True
			ret += str(item)
		return ret + "]"
	#

	def __repr__(self):
		return self.__str__()
	#

	def push(self, item):
		self._data.append(item)
	#

	def pop(self):
		if len(self._data) == 0:
			raise Exception("No item to pop!")
		ret = self._data[len(self._data) - 1]
		self._data = self._data[0:-1]
		return ret
	#

	def mark(self):
		return Stack._Mark(self, len(self._data))
	#

#








