#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_function.py                                                             #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Function class                                                                        #
#                                                                                                 #
# 3.0.6 26-01-2022: removed list type decorators to remove python version dependancy (>=3.8.4)    
###################################################################################################

"""PFunction class implementation, this class is used by the scope and by the interpreter."""

from .macal_parsernodes import ast_Block, ast_function_Param_list

class MacalFunction:
	"""PFunction initialization."""
	def __init__(self, name: str, args: list, block):
		self.name:        str = name
		self.args:        ast_function_Param_list = args
		self.block:       ast_Block = block
		self.scope  = None
		self.is_extern:   bool = False
		self.call_extern: bool = None
