



from ..Stack import Stack
from ..TypedValue import TypedValue





#
# Abstract base class for all token pattern classes.
#
class AbstractTokenPattern(object):

	def __init__(self):
		self.__tags = None
	#

	#
	# Tries to match at the specified position.
	#
	# @param		list tokens				The list of tokens.
	# @param		int offset				Where to try a match.
	# @param		dict defaults			A set of defaults the return data map should be populated with.
	# @return		tuple					Returns a tuple containing the following data:
	#										* bool ---- Indicates success or failure
	#										* int ---- The number of tokens eaten, <c>0</c> if nothing could be eaten
	#										* dict ---- A dictionary containing the parsed data or <c>None</c> if nothing could be eaten
	#
	def tryMatch(self, tokens, offset = 0, defaults = None):
		assert isinstance(tokens, list)
		assert isinstance(offset, int)
		assert isinstance(defaults, (type(None), dict))

		stack = Stack()
		(bResult, n) = self._tryMatch(tokens, offset, stack)
		#print("---- tryMatch: " + str(bResult) + ", " + str(n))
		if bResult:
			ret = {
				"lineNo": tokens[offset].lineNo,
				"colNo": tokens[offset].colNo,
			}
			if defaults != None:
				ret.update(defaults)

			for (entryType, a, b, c) in stack:

				if (entryType == "v") or (entryType == "vv") or (entryType == "d"):

					# there is a value to store.

					# step 1: get the data to store
					if entryType == "d":
						# pure data
						value, varName, bVarIsArray = a, b, c
					elif entryType == "v":
						# take value as is
						token, varName, bVarIsArray = a, b, c
						value = token.value
					else:
						# add typed value
						token, varName, bVarIsArray = a, b, c
						value = TypedValue(token.type, token.value)

					# step 2: actually store the value
					v = ret.get(varName, None)
					if v is None:
						if bVarIsArray:
							ret[varName] = [ value ]
						else:
							ret[varName] = value
					else:
						if isinstance(v, list):
							v.append(value)
							ret[varName] = v
						else:
							ret[varName] = [ v, value ]

				elif entryType == "t":
					a, varName, value = a, b, c
					ret[varName] = value

				else:
					raise Exception("Implementation Error!")

			return (True, n, ret)
		else:
			return (False, 0, None)
	#

	@property
	def tags(self):
		if self.__tags != None:
			return dict(self.__tags)
		else:
			return None
	#

	#
	# Associate a key with a value at this pattern. If parsing succeeds the result data map will receive this key-value-pair.
	#
	def setTag(self, tagName, tagValue):
		if self.__tags is None:
			self.__tags = {}
		self.__tags[tagName] = tagValue
		return self
	#

	def _addTagsToStack(self, stack):
		if self.__tags != None:
			for tagName in self.__tags.keys():
				stack.push(("t", None, tagName, self.__tags[tagName]))
	#

	def _tryMatch(self, tokens, pos, stack):
		pass
	#

	#
	# Derive a pattern from this pattern with specific variations.
	#
	# @param	str assignToVar				If set the result data map will receive the value directly as it is.
	# @param	str assignToVarTyped		If set the result data map will receive the value wrapped in an instance of <c>TypedValue</c>.
	# @param	bool bVarIsArray			Normally values in the result data map will be wrapped into an array only if multiple values occur with the
	#										same key. If this argument is set to <c>True</c> an array is created by default, even if it will receive only one
	#										value. This is useful if the values parsed will represent array data anyway.
	#
	def derive(self, assignToVar = None, assignToVarTyped = None, bVarIsArray = False):
		pass
	#

#






