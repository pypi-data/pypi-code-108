



import typing

from .XLineFragment import XLineFragment
from .ITextBlock import ITextBlock







#
# This is just an adapter to use common layout algorithms by emulating a horizontal list of blocks.
#
class _LayoutAdapter(object):

	#
	# @param		_Column[] columns		A set of vertical columns.
	#
	def __init__(self, nColumnGap:int, columns:list):
		self.nColumnGap = nColumnGap
		self.columns = columns
	#

	@property
	def columnBlocks(self) -> list:
		return self.columns
	#

#

class _Column(object):

	def __init__(self, columnCells:list):
		self.__columnCells = columnCells

		tempMin = []
		tempMax = []
		for x in self.__columnCells:
			tempMin.append(x.minWidth)
			tempMax.append(x.maxWidth)

		self.minWidth = min(tempMin)
		self.maxWidth = max(tempMax)
	#

	def layout(self, availableWidth:int):
		for cell in self.__columnCells:
			if cell:
				cell.layout(availableWidth)
	#

#







#
# This is a block of text consisting of columns.
#
class TextGridBlock(ITextBlock):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, indent:int, rowGap:int, columnGap:int, layouter):
		self.__indent = indent

		self.__rows = []

		self.__nColumnGap = columnGap
		self.__nRowGap = rowGap

		assert callable(layouter)
		self.__layouter = layouter

		# ----

		self.__cached_minWidth = None
		self.__cached_maxWidth = None
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
		return max([ len(row) for row in self.__rows ])
	#

	@property
	def nRows(self) -> int:
		return len(self.__rows)
	#

	#
	# The gap between two columns
	#
	@property
	def nColumnGap(self) -> int:
		return self.__nColumnGap
	#

	@property
	def nRowGap(self) -> int:
		return self.__nRowGap
	#

	@property
	def indent(self) -> int:
		return self.__indent
	#

	@property
	def preferredWidth(self) -> typing.Union[int,None]:
		return self.__preferredWidth
	#

	@property
	def minWidth(self) -> int:
		if self.__cached_minWidth is None:
			self.__cached_minWidth = 0
			for row in self.__rows:
				w = self.__indent + sum([ b.minWidth for b in row ]) + self.__nColumnGap * (self.__nColumns - 1)
				if w > self.__cached_minWidth:
					self.__cached_minWidth = w
		return self.__cached_minWidth
	#

	@property
	def maxWidth(self) -> int:
		if self.__cached_maxWidth is None:
			self.__cached_maxWidth = 0
			for row in self.__rows:
				w = self.__indent + sum([ b.maxWidth for b in row ]) + self.__nColumnGap * (self.__nColumns - 1)
				if w > self.__cached_maxWidth:
					self.__cached_maxWidth = w
		return self.__cached_maxWidth
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	def layout(self, availableWidth:int):
		self.__preferredWidth = availableWidth

		columns = []
		for x in range(0, self.nColumns):
			cells = []
			for y in range(0, self.nRows):
				cells.append(self.__rows[y][x])
			columns.append(_Column(cells))

		li = _LayoutAdapter(self.__nColumnGap, columns)
		self.__layouter(availableWidth, li)
	#

	def addRow(self, cells:typing.Union[list,tuple]):
		self.__rows.append(cells)

		self.__cached_maxWidth = None
		self.__cached_minWidth = None
		self.__preferredWidth = None
	#

	#
	# @return		XLineFragment[]		Returns a list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		lines = []

		for iRow, row in enumerate(self.__rows):
			if iRow > 0:
				# 2nd row or later => add gap
				for i in range(0, self.__nRowGap):
					lines.append(XLineFragment(0, "", 0))

			xPos = self.__indent
			currentLines = []
			for block in row:
				for i, blockLine in enumerate(block.getLines(bColor)):
					if i >= len(currentLines):
						currentLines.append(XLineFragment(0, "", 0))
					currentLines[i] = currentLines[i].join(xPos, blockLine)
				xPos += block.preferredWidth + self.__nColumnGap
			lines.extend(currentLines)

		return lines
	#

#



