


import typing

from .XLineFragment import XLineFragment
from .ITextBlock import ITextBlock





_RESET = "\x1b[0m"





class TextBlockSequence(ITextBlock):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	def __init__(self, indent:int, blockGap:int):
		self.__indent = indent

		self.__blocks = []

		self.__nBlockGap = blockGap

		# ----

		self.__cached_minWidth = None
		self.__cached_maxWidth = None
		self.__preferredWidth = None
	#

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def nBlocks(self) -> int:
		return len(self.__blocks)
	#

	@property
	def nBlockGap(self) -> int:
		return self.__nBlockGap
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
			for b in self.__blocks:
				w = self.__indent + b.minWidth
				if w > self.__cached_minWidth:
					self.__cached_minWidth = w
		return self.__cached_minWidth
	#

	@property
	def maxWidth(self) -> int:
		if self.__cached_maxWidth is None:
			self.__cached_maxWidth = 0
			for b in self.__blocks:
				w = self.__indent + b.maxWidth
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

		w = availableWidth - self.__indent
		for block in self.__blocks:
			block.layout(w)
	#

	def addBlock(self, block):
		self.__blocks.append(block)

		self.__cached_maxWidth = None
		self.__cached_minWidth = None
		self.__preferredWidth = None
	#

	#
	# @return		XLineFragment[]		Returns a list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		lines = []

		for iBlock, block in enumerate(self.__blocks):
			if iBlock > 0:
				# 2nd block or later => add gap
				for i in range(0, self.__nBlockGap):
					lines.append(XLineFragment(0, "", 0))

			for blockLine in block.getLines(bColor):
				blockLine = blockLine.addIndent(self.__indent)
				lines.append(blockLine)

		return lines
	#

#



