#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_interpreterconsts.py                                                    #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Interpreter class constants                                                           #
#                                                                                                 #
# 3.0.6 26-01-2022: removed list type decorators to remove python version dependancy (>=3.8.4)    
###################################################################################################

from collections import namedtuple

"""Interpreter class constant values"""

EXIT_VAR_NAME = 'exit_code'

"""Used specifically for the select command"""
SelectFieldFilter = namedtuple("SelectFilter", ["field_name", "as_name"])
FuncArg = namedtuple("FuncArg", ["arg_name", "arg_type"])