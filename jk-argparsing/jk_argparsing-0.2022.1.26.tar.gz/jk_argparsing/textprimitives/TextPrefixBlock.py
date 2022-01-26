


import typing

from .XLineFragment import XLineFragment
from .ITextBlock import ITextBlock







#
# Instances of this class represent a block of text. This is typically a paragraph.
#
class TextPrefixBlock(ITextBlock):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, indent:int, prefix:str, block):
		self.__indent = indent
		self.__prefix = prefix
		self.__block = block

		self.__preferredWidth = None
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# The preferred with including the indentation
	#
	@property
	def preferredWidth(self) -> typing.Union[int,None]:
		return self.__preferredWidth
	#

	@property
	def maxWidth(self) -> int:
		return self.__indent + len(self.__prefix) + self.__block.maxWidth
	#

	@property
	def minWidth(self) -> int:
		return self.__indent + len(self.__prefix) + self.__block.minWidth
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def layout(self, availableWidth:int):
		w = availableWidth - self.__indent - len(self.__prefix)
		self.__block.layout(w)
	#

	#
	# @return		XLineFragment[]		Returns a list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		templateLine = XLineFragment(self.__indent, self.__prefix, len(self.__prefix))
		retLines = []
		for line in self.__block.getLines(bColor):
			retLines.append(templateLine.append(line))
		return retLines
	#

#



