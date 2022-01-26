



import typing

from .XLineFragment import XLineFragment
from .ITextBlock import ITextBlock









#
# This is a block of text consisting of columns.
#
class TextColumnsBlock(ITextBlock):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, indent:int, columnBlocks:typing.Union[list,tuple], columnGap:int, layouter):
		assert columnBlocks

		self.__indent = indent

		self.__nColumnGap = columnGap
		self.__columnBlocks = columnBlocks
		self.__nColumns = len(columnBlocks)			# the number of columns

		assert callable(layouter)
		self.__layouter = layouter

		# ----

		self.__minWidth = indent + sum([ b.minWidth for b in columnBlocks ]) + columnGap * (self.__nColumns - 1)
		self.__maxWidth = indent + sum([ b.maxWidth for b in columnBlocks ]) + columnGap * (self.__nColumns - 1)
		self.__preferredWidth = None
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	#
	# Returns the number of columns.
	#
	@property
	def nColumns(self) -> int:
		return self.__nColumns
	#

	#
	# The gap between two columns
	#
	@property
	def nColumnGap(self) -> int:
		return self.__nColumnGap
	#

	@property
	def indent(self) -> int:
		return self.__indent
	#

	@property
	def columnBlocks(self) -> list:
		return self.__columnBlocks
	#

	@property
	def preferredWidth(self) -> typing.Union[int,None]:
		#if self.__preferredWidth is None:
		#	return self.__indent + sum([ block.preferredWith for block in self.__columnBlocks ]) + (self.__nColumns - 1) * self.__columnGap
		return self.__preferredWidth
	#

	@property
	def minWidth(self) -> int:
		return self.__minWidth
	#

	@property
	def maxWidth(self) -> int:
		return self.__maxWidth
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	def layout(self, availableWidth:int):
		self.__preferredWidth = availableWidth
		self.__layouter(availableWidth, self)
	#

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# @return		XLineFragment[]		Returns a list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		lines = []
		xPos = self.__indent
		for block in self.__columnBlocks:
			for i, blockLine in enumerate(block.getLines(bColor)):
				if i >= len(lines):
					lines.append(XLineFragment(0, "", 0))
				lines[i] = lines[i].join(xPos, blockLine)
			xPos += block.preferredWidth + self.__nColumnGap

		return lines
	#

#



