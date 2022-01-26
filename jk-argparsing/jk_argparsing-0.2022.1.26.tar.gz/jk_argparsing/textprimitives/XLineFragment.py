




#
# This class represents a part of a single line. It is the result of an output process of a text model,
# not part of the model itself.
#
class XLineFragment(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, indent:int, text:str, textLength:int):
		assert textLength >= 0

		self.__indent = indent
		self.__text = text
		self.__textLength = textLength
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def lineLength(self) -> int:
		return self.__indent + self.__textLength
	#

	@property
	def textLength(self) -> int:
		return self.__textLength
	#

	@property
	def text(self) -> str:
		return self.__text
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def __str__(self):
		if self.__text:
			return " " * self.__indent + self.__text
		else:
			return ""
	#

	def __repr__(self):
		return "XLineFragment<(indent={},text={},textLength={})>".format(self.__indent, repr(self.__text), self.__textLength)
	#

	def addIndent(self, indent:int):
		return XLineFragment(self.__indent + indent, self.__text, self.__textLength)
	#

	def join(self, position:int, other):
		assert isinstance(position, int)
		assert isinstance(other, XLineFragment)

		nPadding = position - self.__textLength
		# print("!!", position, self.__textLength, nPadding)
		if nPadding < 0:
			raise Exception("Line too long: " + str(nPadding) + ", " + repr(self.__text))
		otherIndent = " " * other.__indent
		return XLineFragment(
			self.__indent,
			self.__text + " " * nPadding + otherIndent + other.__text,
			self.__textLength + nPadding + len(otherIndent) + other.__textLength)
	#

	def append(self, other):
		assert isinstance(other, XLineFragment)

		otherIndent = " " * other.__indent
		return XLineFragment(
			self.__indent,
			self.__text + otherIndent + other.__text,
			self.__textLength + len(otherIndent) + other.__textLength)
	#

#



