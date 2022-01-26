


import typing

from .TBlock import TBlock





class TSection(object):

	################################################################################################################################
	## Constructor
	################################################################################################################################

	#
	# Constructor method.
	#
	# @param		str title				The title of this section
	# @param		(str|TBlock|TSection)[] contentBlocks		The paragraphs of this section
	#
	def __init__(self, title:str, contentBlocks:typing.Sequence):
		assert isinstance(title, str)
		assert title
		self.__title = title

		self.__contentBlocks = []
		if contentBlocks:
			for content in contentBlocks:
				self.addContentBlock(content)
	#

	################################################################################################################################
	## Public Properties
	################################################################################################################################

	@property
	def title(self) -> str:
		return self.__title
	#

	@property
	def contentBlocks(self) -> list:
		return list(self.__contentBlocks)
	#

	################################################################################################################################
	## Helper Methods
	################################################################################################################################

	################################################################################################################################
	## Public Methods
	################################################################################################################################

	#
	# @param		str|TBlock|TSection content			The content to add
	#
	def addContentBlock(self, content):
		b = None
		if isinstance(content, TBlock):
			b = content
		elif isinstance(content, TSection):
			b = content
		elif isinstance(content, str):
			b = TBlock(content)
		else:
			raise Exception("Unknown data type used for content: " + type(content).__name__)
		self.__contentBlocks.append(b)
	#

#













