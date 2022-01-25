



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# A token pattern repeat pattern. The specified patteren must match at least once.
#
# @param		AbstractTokenPattern tokenPattern			(required) A token pattern that might be repeated multiple times.
#
class TokenPatternDelimLoop(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern tokenPattern			(required) A token pattern to match one or more times.
	#
	def __init__(self, tokenPattern:AbstractTokenPattern, delimPattern:AbstractTokenPattern):
		super().__init__()

		assert isinstance(tokenPattern, AbstractTokenPattern)
		self.__tokenPattern = tokenPattern

		assert isinstance(delimPattern, AbstractTokenPattern)
		self.__delimPattern = delimPattern
	#

	def _tryMatch(self, tokens, pos, stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		orgPos = pos

		(bResult, n) = self.__tokenPattern._tryMatch(tokens, pos, stack)
		if not bResult:
			return (False, 0)
		pos += n

		lastGoodPos = pos
		nCountLoops = 1

		while True:
			(bResult, n) = self.__delimPattern._tryMatch(tokens, pos, stack)
			if not bResult:
				break
			pos += n

			(bResult, n) = self.__tokenPattern._tryMatch(tokens, pos, stack)
			if not bResult:
				pos = lastGoodPos
				break
			pos += n

			nCountLoops += 1
			lastGoodPos = pos

		self._addTagsToStack(stack)
		return (True, pos - orgPos)
	#

	#
	# Derive a new token pattern from this object, modifying some attributes in the process.
	#
	def derive(self, assignToVar:str = None, assignToVarTyped:str = None, bVarIsArray:bool = False):
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		return TokenPatternDelimLoop(self.__tokenPattern.derive(assignToVar, assignToVarTyped, bVarIsArray))
	#

#






