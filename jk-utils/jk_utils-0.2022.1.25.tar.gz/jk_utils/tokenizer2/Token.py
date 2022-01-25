


import collections



#
# This defines a token data structure. This structure has the following fields:
#
# @attribute		str type		A type identifier that specifies the type of the token
# @attribute		obj value		The value of the token (can be of any data type)
# @attribute		int lineNo		The line number (counted from 1)
# @attribute		int colNo		The character number within the line (counted from 1)
#
Token = collections.namedtuple("Token", ["type", "value", "lineNo", "colNo", "length"])






