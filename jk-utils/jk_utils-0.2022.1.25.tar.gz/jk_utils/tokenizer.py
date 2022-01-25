


import re
import collections

from .Stack import Stack
from .TypedValue import TypedValue







#
# This defines a token data structure. This structure has the following fields:
#
# @attribute		str type		A type identifier that specifies the type of the token
# @attribute		obj value		The value of the token (can be of any data type)
# @attribute		int lineNo		The line number (counted from 1)
# @attribute		int colNo		The character number within the line (counted from 1)
#
Token = collections.namedtuple('Token', ['type', 'value', 'lineNo', 'colNo'])






#
# RegEx based tokenizer: This tokenizer uses regular expressions in order to create tokens.
#
class RegExBasedTokenizer(object):

	#
	# Initialization method
	#
	# @param		str[] patternDefs		A list of pattern definitions. Each pattern definition should be a tuple or list of one of the following structures:
	#										* 2 items
	#											* (required) the token type to use on match
	#											* (required) the pattern to match
	#										* 4 items
	#											* (required) the token type to use on match
	#											* (optional) if not None a pattern to match but that will not be part of the token content
	#											* (required) the pattern to match (which will be the content of the token)
	#											* (optional) if not None a pattern to match but that will not be part of the token content
	#
	def __init__(self, patternDefs):
		assert isinstance(patternDefs, (tuple, list))
		assert len(patternDefs) > 0

		p = ""
		for patternDef in patternDefs:
			assert isinstance(patternDef, (tuple, list))
			if len(p) > 0:
				p += "|"
			if len(patternDef) == 2:
				p += '(?P<' + patternDef[0] + '>' + patternDef[1] + ')'
			elif len(patternDef) == 4:
				if patternDef[1] != None:
					p += '(?:' + patternDef[1] + ')'
				p += '(?P<' + patternDef[0] + '>' + patternDef[2] + ')'
				if patternDef[3] != None:
					p += '(?:' + patternDef[3] + ')'
			else:
				raise Exception("Invalid pattern definition: " + str(patternDef))

		self.__rawPatterns = p
		self.__compiledPatterns = None
		self.__typeParsingDelegates = {}
	#



	@property
	def isCompiled(self):
		return self.__compiledPatterns != None
	#



	def compile(self):
		rawPatterns = self.__rawPatterns
		rawPatterns += "|(?P<NEWLINE>\n)"
		rawPatterns += "|(?P<SPACE>[\t ]+)"
		rawPatterns += "|(?P<ERROR>.)"
		try:
			self.__compiledPatterns = re.compile(rawPatterns)
		except Exception as e:
			print("==== COMPILE ERROR")
			print("==== " + e.msg)
			print("==== " + rawPatterns)
			s = ""
			for i in range(0, e.colno):
				s += " "
			s += "^"
			print(s)
			raise
	#



	def addTokenPattern(self, tokenType:str, patternRegExStr):
		assert isinstance(tokenType, str)

		bErr = False
		if isinstance(patternRegExStr, (tuple, list)):
			if len(patternRegExStr) == 1:
				if isinstance(patternRegExStr[0], str):
					patternRegExStr = patternRegExStr[0]
				else:
					bErr = True
			elif len(patternRegExStr) == 3:
				pass
			else:
				bErr = True
		elif isinstance(patternRegExStr, str):
			pass
		else:
			bErr = True
		if bErr:
			raise Exception("Invalid patternRegExStr specified!")

		if len(self.__rawPatterns) > 0:
			self.__rawPatterns += "|"
		if isinstance(patternRegExStr, str):
			self.__rawPatterns += '(?P<' + tokenType + '>' + patternRegExStr + ')'
		else:
			if patternRegExStr[0] != None:
				self.__rawPatterns += '(?:' + patternRegExStr[0] + ')'
			self.__rawPatterns += '(?P<' + tokenType + '>' + patternRegExStr[1] + ')'
			if patternRegExStr[2] != None:
				self.__rawPatterns += '(?:' + patternRegExStr[2] + ')'

		self.__compiledPatterns = None
	#



	def registerTypeParsingDelegate(self, tokenTypeMain, tokenTypeExtra, delegate):
		assert isinstance(tokenTypeMain, str)
		assert isinstance(tokenTypeExtra, (type(None), str))
		assert callable(delegate)

		if tokenTypeExtra is None:
			tokenType = tokenTypeMain
		else:
			tokenType = tokenTypeMain + "_" + tokenTypeExtra
		self.__typeParsingDelegates[tokenType] = delegate
	#



	#
	# @return		Token[] tokens			Returns token objects according to the pattern defined during initialization.
	#
	def tokenize(self, text, bEmitWhiteSpaces = False, bEmitNewLines = False):
		if not self.isCompiled:
			self.compile()

		lineNo = 1
		line_start = 0
		for mo in self.__compiledPatterns.finditer(text):
			tokenType = mo.lastgroup
			value = mo.group(tokenType)
			columnNo = mo.start() - line_start + 1
			if tokenType == 'NEWLINE':
				if bEmitNewLines:
					yield Token(tokenType, value, lineNo, columnNo)
				line_start = mo.end()
				lineNo += 1
			elif tokenType == 'SPACE':
				if bEmitWhiteSpaces:
					yield Token(tokenType, value, lineNo, columnNo)
			elif tokenType == 'ERROR':
				raise RuntimeError("Tokenization error encountered at " + str(lineNo) + ":" + str(columnNo) + "!")
			else:
				d = self.__typeParsingDelegates.get(tokenType, None)
				if d != None:
					value = d(value)
				pos = tokenType.find("_")
				# tokenTypeExtra = None
				#if pos >= 0:
					#tokenTypeExtra = tokenType[pos + 1:]
					#tokenType = tokenType[0:pos]
				# s = "" if tokenTypeExtra == None else tokenTypeExtra
				# print("---- " + tokenTypeMain + ":" + s + " ---- \"" + tokenText + "\"")
				if pos >= 0:
					tokenType = tokenType[0:pos]
				yield Token(tokenType, value, lineNo, columnNo)
	#



	#
	# Override this method to perform correct value parsing. This method is called for every
	#
	def _parseValue(self, tokenTypeMain, tokenTypeExtra, tokenText):
		return tokenText
	#

#






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

				if (entryType == "v") or (entryType == "vv"):

					# there is a value to store.

					# step 1: get the data to store
					token, varName, bVarIsArray = a, b, c
					if entryType == "v":
						value = token.value
					else:
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






#
# A token pattern optional pattern. The specified patteren must match either zero times or once.
#
class TokenPatternOptional(AbstractTokenPattern):

	#
	# @param		AbstractTokenPattern tokenPattern			(required) A token patterns to match against.
	#
	def __init__(self, tokenPattern):
		super().__init__()

		assert isinstance(tokenPattern, AbstractTokenPattern)
		self.__tokenPattern = tokenPattern
	#

	def _tryMatch(self, tokens, pos, stack):
		assert isinstance(tokens, list)
		assert isinstance(pos, int)
		assert isinstance(stack, Stack)

		(bResult, n) = self.__tokenPattern._tryMatch(tokens, pos, stack)
		assert isinstance(bResult, bool)
		assert isinstance(n, int)

		self._addTagsToStack(stack)
		return (True, n)
	#

	def derive(self, assignToVar = None, assignToVarTyped = None, bVarIsArray = False):
		assert isinstance(assignToVar, (type(None), str))
		assert isinstance(assignToVarTyped, (type(None), str))
		assert isinstance(bVarIsArray, bool)

		return TokenPatternOptional(self.__tokenPattern.derive(assignToVar, assignToVarTyped, bVarIsArray))
	#

#







