



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# A token sequence pattern. The complete sequence must match, regardless of what kind of element it consists.
#
class TokenPatternSequence(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern[] tokenPatterns			(required) A sequence of token patterns to match against.
	#
	def __init__(self, tokenPatterns:list):
		super().__init__()

		assert isinstance(tokenPatterns, list)
		for t in tokenPatterns:
			assert isinstance(t, AbstractTokenPattern)
		self.__tokenPatterns = tokenPatterns
		self.__len = len(tokenPatterns)
	#

	def _tryMatch(self, tokens, pos, stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		m = stack.mark()
		orgPos = pos
		for i in range(0, self.__len):
			(bResult, n) = self.__tokenPatterns[i]._tryMatch(tokens, pos, stack)
			assert isinstance(bResult, bool)
			assert isinstance(n, int)

			if not bResult:
				m.resetToMark()
				return (False, 0)
			pos += n
		if pos - orgPos > 0:
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

		tokenPatterns = []
		for tokenPattern in self.__tokenPatterns:
			tokenPatterns.append(tokenPattern.derive(assignToVar, assignToVarTyped, bVarIsArray))
		return TokenPatternSequence(tokenPatterns)
	#

#






