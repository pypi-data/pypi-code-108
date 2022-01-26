#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_exprtypes.py                                                            #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Expression Type names                                                                 #
#
# 3.0.6 26-01-2022: removed list type decorators to remove python version dependancy (>=3.8.4)    
#                                                                                                 #
###################################################################################################

"""constants used as type names for expression nodes."""

BINARY      = "BINARY"
UNARY       = "UNARY"
LITERAL     = "LITERAL"
GROUPING    = "GROUPING"
VARIABLE    = "VARIABLE"
INDEX       = "INDEX"
PARAMS      = "PARAMS"
FUNCTION    = "FUNCTION"
CALL        = "CALL"