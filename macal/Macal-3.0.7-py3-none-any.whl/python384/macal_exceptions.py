#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_exceptions.py                                                           #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Exceptions                                                                            #
#                                                                                                 #
###################################################################################################

"""Exceptions classes for macal 2.0"""

from .macal_scope import MacalScope

class InvalidFunctionCallException(Exception):
    def __init__(self, name: str, funcname: str, scope: MacalScope):
        self.Name = name
        self.Scope = scope
        self.FuncName = funcname

    def __str__(self):
        return f"Invalid function call: {self.Name}, expected {self.FuncName}. {self.Scope.name}";

class InvalidParamCountException(Exception):
    def __init__(self, name: str, scope: MacalScope, length: int, required: int):
        self.Name = name
        self.Scope = scope
        self.Length = length
        self.Required = required

    def __str__(self):
        return f"{self.Name}: Invalid number of parameters provided: {self.Length}, required: {self.Required}. ({self.Scope.name})"

class MissingParameterException(Exception):
    def __init__(self, name: str, scope: MacalScope, param_name: str, func_name: str = ""):
        self.Name = name
        self.Scope = scope
        self.ParamName = param_name
        self.FuncName = func_name
        
    def __str__(self):
        if self.Scope is None:
            return f"{self.Name}: Function parameter missing: {self.ParamName}. {self.FuncName}"
        else:
            return f"{self.Name}: Function parameter missing: {self.ParamName}. ({self.Scope.name}) {self.FuncName}"

class InvalidParamTypeException(Exception):
    def __init__(self, name: str, scope: MacalScope, param_name: str, invalid_type: str, required_type: str):
        self.Name = name
        self.Scope = scope
        self.ParamName = param_name
        self.InvalidType = invalid_type
        self.RequiredType = required_type
        
    def __str__(self):
        return f"{self.Name}: Invalid parameter ({self.ParamName}) type: {self.InvalidType}, required: {self.RequiredType}. ({self.Scope.name})"

class VariableNotFoundException(Exception):
    def __init__(self, name: str, scope: MacalScope):
        self.Name = name
        self.Scope = scope
        
    def __str__(self):
        return f"Exception: Variable not found ({self.Name}). ({self.Scope.name})"

class InvalidVariableTypeException(Exception):
    def __init__(self, name: str, scope: MacalScope, invalid_type: str, required_type: str):
        self.Name = name
        self.Scope = scope
        self.InvalidType = invalid_type
        self.RequiredType = required_type
        
    def __str__(self):
        return f"Exception: Invalid variable ({self.Name}) type: {self.InvalidType}, required: {self.RequiredType}. ({self.Scope.name})"

class RuntimeError(Exception):
    def __init__(self, message: str):
        self.Message = message
        
    def __str__(self):
        return f"Runtime Error: {self.Message}"

class LexException(Exception):
    def __init__(self, message: str, line: int, offset: int):
        self.message = message
        self.line = line
        self.offset = offset

    def __repr__(self):
        return f"""LexException("{self.message}", {self.line}, {self.offset})"""

    def __str__(self):
        return f"Lex Exception: {self.message} @ {self.line} , {self.offset}"