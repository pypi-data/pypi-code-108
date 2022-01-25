



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# A token pattern alternative pattern. One of the specified patterns must match.
#
class TokenPatternAlternatives(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern[] tokenPatterns			(required) A set of token patterns to match against.
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
		for i in range(0, self.__len):
			(bResult, n) = self.__tokenPatterns[i]._tryMatch(tokens, pos, stack)
			assert isinstance(bResult, bool)
			assert isinstance(n, int)

			if bResult:
				self._addTagsToStack(stack)
				return (True, n)
			m.resetToMark()
		return (False, 0)
	#

	def derive(self, assignToVar = None, assignToVarTyped = None, bVarIsArray = False):
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		tokenPatterns = []
		for tokenPattern in self.__tokenPatterns:
			tokenPatterns.append(tokenPattern.derive(assignToVar, assignToVarTyped, bVarIsArray))
		return TokenPatternAlternatives(tokenPatterns)
	#

#






