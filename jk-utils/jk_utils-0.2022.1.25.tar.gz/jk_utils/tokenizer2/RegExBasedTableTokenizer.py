


import re
import collections
import typing

from .Token import Token
from .TokenizationError import TokenizationError






class _TokenizationState(object):

	def __init__(self, initialState:str):
		self.lineNo = 1
		self.line_start = 0
		self.pos = 0
		self.currentState = initialState
	#

#




#
# RegEx based tokenizer: This tokenizer uses regular expressions in order to create tokens.
#
class RegExBasedTokenizingTable(object):

	#
	# Initialization method
	#
	# @param		object[] patternDefs	A list of pattern definitions. Each pattern definition should be a tuple or list of one of the following structures:
	#										* 4 items
	#											* (required) str: the token type to use on match
	#											* (required) str: the pattern to match
	#											* (optional) str: next state
	#											* (optional) callable: parsing delegate
	#										* 6 items
	#											* (required) str: the token type to use on match
	#											* (optional) str: if not None a pattern to match but that will not be part of the token content
	#											* (required) str: the pattern to match (which will be the content of the token)
	#											* (optional) str: if not None a pattern to match but that will not be part of the token content
	#											* (optional) str: next state
	#											* (optional) callable: parsing delegate
	#
	def __init__(self, stateName:str, patternDefs, bDebug:bool = False):
		assert isinstance(stateName, str)
		assert stateName

		assert isinstance(patternDefs, (tuple, list))
		assert len(patternDefs) > 0

		self.__stateName = stateName

		self.__tokenPseudoTypeToTokenTypeMap = {
			"NEWLINE": "NEWLINE",
			"SPACE": "SPACE",
			"ERROR": "ERROR",
		}

		self.__pattern2StateMap = {}
		self.__tokenParsingDelegatesMap = {}
		rawPatternsList = []
		rawPatternsSources = []
		n = 1
		for patternDef in patternDefs:
			assert isinstance(patternDef, (tuple, list))

			if len(patternDef) == 4:
				tokenType, pattern, nextState, parsingDelegate = patternDef
				patternPre = None
				patternPost = None
			elif len(patternDef) == 6:
				tokenType, patternPre, pattern, patternPost, nextState, parsingDelegate = patternDef
			else:
				raise Exception("Invalid pattern definition: " + str(patternDef))
			tokenPseudoType = tokenType + "_" + str(n)
			self.__tokenPseudoTypeToTokenTypeMap[tokenPseudoType] = tokenType

			p2 = []
			if patternPre:
				p2.extend(("(?:", patternPre, ")"))
			p2.extend(("(?P<", tokenPseudoType, ">", pattern, ")"))
			if patternPost:
				p2.extend(("(?:", patternPost, ")"))

			rawPatternsList.append("".join(p2)),
			rawPatternsSources.append(tokenType)
			self.__pattern2StateMap[tokenPseudoType] = nextState
			self.__tokenParsingDelegatesMap[tokenPseudoType] = parsingDelegate

			n += 1

		self.__compiledPatterns = None

		if bDebug:
			print("Compiling regular expressions for " + self.__class__.__name__ + " state " + repr(stateName) + ":")
			for tt, r in zip(rawPatternsSources, rawPatternsList):
				print("\t" + repr(tt) + "\t\t=>  " + repr(r))

		rawPatterns = "|".join(rawPatternsList)
		rawPatterns += "|(?P<NEWLINE>\n)"
		rawPatterns += "|(?P<SPACE>[\t ]+)"
		rawPatterns += "|(?P<ERROR>.)"
		try:
			self.__compiledPatterns = re.compile(rawPatterns)
			if bDebug:
				print("\tPATTERN: " + rawPatterns)
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



	def addStateTransition(self, tokenType:str, nextState:str):
		self.__pattern2StateMap[tokenType] = nextState
		return self
	#



	@property
	def stateName(self):
		return self.__stateName
	#



	def _getNextToken(self, state:_TokenizationState, text:str) -> tuple:
		mo = self.__compiledPatterns.match(text, state.pos)
		columnNo = state.pos - state.line_start + 1
		if not mo:
			raise TokenizationError("No RegEx match", state.lineNo, columnNo, state.currentState)
		if state.pos != mo.start():
			raise TokenizationError("Invalid RegEx match pos", state.lineNo, columnNo, state.currentState)

		tokenPseudoType = mo.lastgroup
		value = mo.group(tokenPseudoType)
		tokenType = self.__tokenPseudoTypeToTokenTypeMap[tokenPseudoType]
		if tokenType == "NEWLINE":
			ret = Token(tokenType, value, state.lineNo, columnNo, mo.end() - state.pos)
			state.line_start = mo.end()
			state.lineNo += 1
		elif tokenType == "SPACE":
			ret = Token(tokenType, value, state.lineNo, columnNo, mo.end() - state.pos)
		elif tokenType == "ERROR":
			raise TokenizationError("Error match", state.lineNo, columnNo, state.currentState)
		else:
			d = self.__tokenParsingDelegatesMap.get(tokenPseudoType)
			if d != None:
				value = d(value)
			ret = Token(tokenType, value, state.lineNo, columnNo, mo.end() - state.pos)
			if tokenType == 'newline':
				state.line_start = mo.end()
				state.lineNo += 1

		#print(">>EMITTING:", ret)
		nextState = self.__pattern2StateMap.get(tokenPseudoType)
		if nextState:
			#print(">>SWITCHING FROM STATE", repr(state.currentState), "TO STATE", repr(nextState))
			state.currentState = nextState

		state.pos = mo.end()

		return ret
	#



	def _getAllResultStates(self) -> list:
		return [ x for x in self.__pattern2StateMap.values() if x is not None ]
	#



#




class RegExBasedTableTokenizer(object):

	def __init__(self, initialState:str, tokenizationTables:typing.Union[list,tuple,typing.Sequence]):
		assert isinstance(initialState, str)
		assert initialState

		tokenizationTables = list(tokenizationTables)
		self.__tokenizationTableMap = {}

		allStates = set()
		allResultStates = set()
		for table in tokenizationTables:
			assert isinstance(table, RegExBasedTokenizingTable)
			if table.stateName in self.__tokenizationTableMap:
				raise Exception("Duplicate table: " + table.stateName)
			for s in table._getAllResultStates():
				allResultStates.add(s)
			allStates.add(table.stateName)
			self.__tokenizationTableMap[table.stateName] = table
		#print("allStates:", allStates)
		#print("allResultStates:", allResultStates)
		wrongResultStates = allResultStates - allStates
		if wrongResultStates:
			raise Exception("No such states: " + str(sorted(wrongResultStates)))

		if initialState not in self.__tokenizationTableMap:
			raise Exception("No such initial state: " + repr(initialState))

		self.__initialState = initialState
	#



	#
	# @return		Token,str[] tokens			Returns token objects according to the pattern defined during initialization.
	#
	def tokenize(self, text, bEmitWhiteSpaces:bool = False, bEmitNewLines:bool = False):
		assert isinstance(text, str)
		assert isinstance(bEmitWhiteSpaces, bool)
		assert isinstance(bEmitNewLines, bool)

		state = _TokenizationState(self.__initialState)
		maxPos = len(text)
		while state.pos < maxPos:
			currentTable = self.__tokenizationTableMap[state.currentState]
			t = currentTable._getNextToken(state, text)
			if t.type.startswith("__"):
				continue
			elif t.type == "NEWLINE":
				if bEmitNewLines:
					yield t
			elif t.type == "SPACE":
				if bEmitWhiteSpaces:
					yield t
			else:
				yield t
	#



#




