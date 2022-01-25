


class TokenizationError(Exception):

	def __init__(self, errMsg:str, lineNo:int, colNo:int, state:str = None):
		s = "Tokenization error encountered at " + str(lineNo) + ":" + str(colNo) + ": " + errMsg
		if state:
			s += " (Current state: " + repr(state) + ")"
		super().__init__(s)
	#

#













