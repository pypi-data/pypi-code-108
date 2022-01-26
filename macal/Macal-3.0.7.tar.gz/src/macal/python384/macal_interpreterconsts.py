#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_interpreterconsts.py                                                    #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Interpreter class constants                                                           #
#                                                                                                 #
###################################################################################################

from collections import namedtuple

"""Interpreter class constant values"""

EXIT_VAR_NAME = 'exit_code'

"""Used specifically for the select command"""
SelectFieldFilter = namedtuple("SelectFilter", ["field_name", "as_name"])
FuncArg = namedtuple("FuncArg", ["arg_name", "arg_type"])