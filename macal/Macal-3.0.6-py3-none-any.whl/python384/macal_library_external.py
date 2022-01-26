#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_external.py                                                     #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 3.0 External Library Imports module                                                       #
# Consolidates many modules so that for library development you only have to import this module.  #
#                                                                                                 #
###################################################################################################

"""library development imports module"""

from .macal_library           import MacalLibrary
from .macal_interpreterconsts import FuncArg
from .macal_scope             import MacalScope
from .macal_function          import MacalFunction
from .macal_exceptions        import RuntimeError
from .macal_parsernodetypes   import VARIABLE
from .macal_variable_types    import ANY, ARRAY, BOOL, FLOAT, INT, PARAMS, RECORD, STRING, FUNCTION
from .macal_keywords          import NIL

__all__ = ['MacalLibrary', 'FuncArg', 'MacalScope', 'MacalFunction', 'VARIABLE', 'ANY', 'ARRAY', 'BOOL', 
		   'FLOAT', 'INT', 'PARAMS', 'RECORD', 'STRING', 'NIL', 'FUNCTION', "RuntimeError"]
