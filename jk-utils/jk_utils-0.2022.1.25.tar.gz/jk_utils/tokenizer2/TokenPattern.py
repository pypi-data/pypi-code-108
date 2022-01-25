



from ..Stack import Stack
from ..TypedValue import TypedValue
from .AbstractTokenPattern import AbstractTokenPattern





#
# An atom-like token pattern.
#
class TokenPattern(AbstractTokenPattern):

	#
	# @param		str tokenType			(required) The type identifier of a token, e.g. "int"
	# @param		str tokenValue			(optional) The text value the token is expected to have for a match.
	# @param		str assignToVar			(optional) On match use the value as the string it is within the token.
	# @param		str assignToVarTyped	(optional) On match use the value but wrap the token text into `TypedValue`,
	#										using the token type as type information for `TypedValue'. Thus this way type information
	#										is preserved.
	# @param		bool bVarIsArray		(optional) This variable is an array. If it is an array, data is stacked as an array.
	#
	def __init__(self, tokenType:str, tokenValue:str = None, assignToVar:str = None, assignToVarTyped:str = None, bVarIsArray:bool = False):
		super().__init__()

		assert isinstance(tokenType, str)
		assert isinstance(tokenValue, (type(None), str))
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		self.__tokenType = tokenType
		self.__tokenValue = tokenValue
		self.__assignToVar = assignToVar
		self.__assignToVarTyped = assignToVarTyped
		self.__bVarIsArray = bVarIsArray
	#

	def _tryMatch(self, tokens:list, pos:int, stack:Stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		if pos >= len(tokens):
			return (False, 0)
		if tokens[pos].type != self.__tokenType:
			return (False, 0)
		if (self.__tokenValue != None) and (tokens[pos].value != self.__tokenValue):
			return (False, 0)
		if self.__assignToVar != None:
			stack.push(("v", tokens[pos], self.__assignToVar, self.__bVarIsArray))
		if self.__assignToVarTyped != None:
			stack.push(("vv", tokens[pos], self.__assignToVarTyped, self.__bVarIsArray))
		self._addTagsToStack(stack)
		return (True, 1)
	#

	#
	# Derive a new token pattern from this object, modifying some attributes in the process.
	#
	def derive(self, assignToVar:str = None, assignToVarTyped:str = None, bVarIsArray:bool = False):
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		return TokenPattern(self.__tokenType, self.__tokenValue, assignToVar, assignToVarTyped, bVarIsArray)
	#

#






