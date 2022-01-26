# Filename:    macal_lextoken.py
# Author:      Marco Caspers
# Version:     3.0
# Description:
#
# Lexer Token Class for Macal Programming Language
#
###################################################################################################

#this is the old 2.0 stuff.
""""Named tuples used for function return values"""

from collections import namedtuple

# Location tuple used to keep track of the location of a token, and/or the current position in the
# source code.
Location = namedtuple('Location', ["pos", "line", "offset"])

# Actual lexer token consists of a type, value and location where location is of type Location to
# indicate where in the source code the token is.
Token = namedtuple('Token', ["type", "value", "location"])

SingleToken = namedtuple("SingleToken", ["value", "type"])

# Used by the parser to split each parameter in the select statement by it's token, astoken and
# asvalue. token being having the name of a field as value or * for any.
# Astoken being the "as" keyword, asvalue being the token that has the destination name of the
# field.
SelectParam = namedtuple('SelectParam', ['token', 'astoken', 'asvalue'])

Some = namedtuple('Some', ['value', 'location'])

def print_token(token: Token):
	print("Token: ")
	print("Type:  ", token.type)
	print("Value: ", token.value)
	print('Pos:   ', token.location.pos)
	print('Line:  ', token.location.line)
	print('Offset:', token.location.offset)

# this is the new 3.0 stuff.
# The token position is an interresting value to store because of useage in syntax highlighting.
# For making things human readable it has no real function though.
# The line and offset are for the first character in the token.

class LexToken:
	def __init__(self, token_type: str, token_value, pos: int, line: int, offset: int):
		self.token_type = token_type
		self.token_value = token_value
		self.token_position = pos
		self.token_line = line
		self.token_offset = offset

	def __repr__(self):
		return (
			f"""LexerToken(token_type = "{self.token_type}", token_value = "{self.token_value}", """ +
			f"token_position = {self.token_position}, token_line = {self.token_line}, " +
			f"token_offset = {self.token_offset})")

	def __str__(self):
		return f"{self.token_type} : {self.token_value} @{self.token_line},{self.token_offset}"


