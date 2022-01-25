


import re
import collections

from .Token import Token






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
				if tokenType == 'newline':
					line_start = mo.end()
					lineNo += 1
	#



	#
	# Override this method to perform correct value parsing. This method is called for every
	#
	def _parseValue(self, tokenTypeMain, tokenTypeExtra, tokenText):
		return tokenText
	#

#









