



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# A token pattern repeat pattern. The specified patteren must match at least once.
#
# @param		AbstractTokenPattern tokenPattern			(required) A token pattern that might be repeated multiple times.
#
class TokenPatternRepeatUntilNot(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern tokenPattern			(required) A token pattern to match one or more times.
	#
	def __init__(self, tokenPattern:AbstractTokenPattern, assignTokensToVar:str = None):
		super().__init__()

		assert isinstance(tokenPattern, AbstractTokenPattern)
		self.__tokenPattern = tokenPattern

		assert isinstance(assignTokensToVar, (type(None), str))
		self.__assignTokensToVar = assignTokensToVar
	#

	def _tryMatch(self, tokens, pos, stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		orgPos = pos

		while True:
			if pos == len(tokens):
				return (False, 0)

			(bResult, n) = self.__tokenPattern._tryMatch(tokens, pos, stack)
			assert isinstance(bResult, bool)
			assert isinstance(n, int)

			if bResult:
				break

			pos += 1

		if self.__assignTokensToVar is not None:
			stack.push(("d", tokens[orgPos:pos], self.__assignTokensToVar, False))
		self._addTagsToStack(stack)
		return (True, pos - orgPos)
	#

#






