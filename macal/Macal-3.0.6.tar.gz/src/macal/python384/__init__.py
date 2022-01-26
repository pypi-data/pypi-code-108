#!/usr/bin/python3
#-------------------------------------------------------------------------------------------------#
# Filename:       | __init__.py                                                                   #
# Author:         | Marco Caspers                                                                 #
# Date:           | 06-01-2022                                                                    #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 3.0 language Initialization                                                               #
#                                                                                                 #
###################################################################################################

"""macal Main class implementation"""

from .macal                 import Macal
from .macal_lexer           import MacalTokenizer
from .macal_parser          import MacalParser
from .macal_interpreter     import MacalInterpreter
from .macal_library         import MacalLibrary
from .macal_scope           import MacalScope
from .macal_library_system  import LibrarySystem
from .macal_library_strings import LibraryStrings
from .macal_library_time    import LibraryTime
from .macal_library_io      import LibraryIO
from .macal_library_syslog  import LibrarySyslog
from .macal_library_csv     import LibraryCsv
from .macal_lextoken        import LexToken
from .macal_function        import MacalFunction

__version__ = "3.0.1"
__author__ = "Marco Caspers"
__credits__ = "Copyright (c) 2022 Westcon Security Netherlands"

__all__ = ['Macal', 'MacalTokenizer', 'MacalParser', 'MacalInterpreter', 'MacalLibrary', 
    'MacalScope', 'LibrarySystem', 'LibraryStrings', 'LibraryTime', 'LibraryIO',
    'LibrarySyslog', 'LibraryCsv', 'LexToken', 'MacalFunction']
