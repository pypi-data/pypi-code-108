



import typing

from .XLineFragment import XLineFragment






class ITextBlock:

	################################################################################################################################
	## Constructor
	################################################################################################################################

	################################################################################################################################
	## Properties
	################################################################################################################################

	@property
	def indent(self) -> int:
		raise NotImplementedError()
	#

	@property
	def preferredWidth(self) -> typing.Union[int,None]:
		raise NotImplementedError()
	#

	@property
	def minWidth(self) -> int:
		raise NotImplementedError()
	#

	@property
	def maxWidth(self) -> int:
		raise NotImplementedError()
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# Layout this component.
	#
	# @param	int availableWidth			The width this component can use for layouting.
	#
	def layout(self, availableWidth:int):
		raise NotImplementedError()
	#

	#
	# Returns a list of lines.
	# Call this method after layouting has been peformed.
	# Otherwise the situation is undefined: *getLines()* might even throw an Exception or might simply return useless data.
	#
	# @return		XLineFragment[]		The list of lines.
	#
	def getLines(self, bColor:bool) -> list:
		raise NotImplementedError()
	#

#



