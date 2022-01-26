


from .XLineFragment import XLineFragment
from .ITextBlock import ITextBlock





_RESET = "\x1b[0m"





#
# Instances of this class represent a sequence of empty lines.
#
class TextEmpty(ITextBlock):

	__EMPTY_LINE = XLineFragment(0, "", 0)

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, nLines:int):
		self.__nLines = nLines
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# The preferred with including the indentation
	#
	@property
	def preferredWidth(self) -> int:
		return 0
	#

	@property
	def maxWidth(self) -> int:
		return 0
	#

	@property
	def minWidth(self) -> int:
		return 0
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def layout(self, availableWidth:int):
		pass
	#

	#
	# @return		XLineFragment[]		Returns a list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		return [ TextEmpty.__EMPTY_LINE ] * self.__nLines
	#

#



