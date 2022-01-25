



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# A token pattern repeat pattern. The specified patteren must match at least once.
#
# @param		AbstractTokenPattern tokenPattern			(required) A token pattern that might be repeated multiple times.
#
class TokenPatternRepeat(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern tokenPattern			(required) A token pattern to match one or more times.
	#
	def __init__(self, tokenPattern:AbstractTokenPattern):
		super().__init__()

		assert isinstance(tokenPattern, AbstractTokenPattern)
		self.__tokenPattern = tokenPattern
	#

	def _tryMatch(self, tokens, pos, stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		orgPos = pos
		nCountLoops = 0
		while True:
			(bResult, n) = self.__tokenPattern._tryMatch(tokens, pos, stack)
			assert isinstance(bResult, bool)
			assert isinstance(n, int)

			if not bResult:
				break
			pos += n
			nCountLoops += 1
		if nCountLoops > 0:
			self._addTagsToStack(stack)
			return (True, pos - orgPos)
		else:
			return (False, 0)
	#

	#
	# Derive a new token pattern from this object, modifying some attributes in the process.
	#
	def derive(self, assignToVar:str = None, assignToVarTyped:str = None, bVarIsArray:bool = False):
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		return TokenPatternRepeat(self.__tokenPattern.derive(assignToVar, assignToVarTyped, bVarIsArray))
	#

#






