#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_system.py                                                       #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Strings Library                                                                       #
#                                                                                                 #
###################################################################################################

"""Strings library implementation"""

from .macal_library_external import *
from unidecode import unidecode

class LibraryStrings(MacalLibrary):
    def __init__(self):
        super().__init__("strings")
        self.RegisterFunction("len",            [FuncArg("arg", ANY)], self.StrLen)
        self.RegisterFunction("left",           [FuncArg("arg", STRING),    FuncArg("length", INT)], self.StrLeft)
        self.RegisterFunction("mid",            [FuncArg("arg", STRING),    FuncArg("start", INT),   FuncArg("length", INT)], self.StrMid)
        self.RegisterFunction("tostring",       [FuncArg("arg", ANY)], self.ToString)
        self.RegisterFunction("format",         [FuncArg("format", STRING), FuncArg("arg", ANY)], self.StrFormat)
        self.RegisterFunction("replace",        [FuncArg("_var", STRING),  FuncArg("from", STRING), FuncArg("with", STRING)], self.StrReplace)
        self.RegisterFunction("startswith",     [FuncArg("haystack", STRING), FuncArg("needle", STRING)], self.StartsWith)
        self.RegisterFunction("removeNonAscii", [FuncArg("text", STRING)], self.RemoveNonAscii)
        self.RegisterFunction("replaceEx",      [FuncArg("_var", STRING),FuncArg("repl", STRING),FuncArg("by", STRING)], self.ReplaceEx)

    def StrLen(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of console function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = len(self.GetParamValue(params, "arg"))
        scope.SetReturnValue(result, INT)
    
    def StrLeft(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of left function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = self.GetParamValue(params, "arg")[0:self.GetParamValue(params, "length")]
        scope.SetReturnValue(result, STRING)

    def StrMid(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of mid function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = self.GetParamValue(params, "arg")[self.GetParamValue(params, "start"):self.GetParamValue(params, "length")]
        scope.SetReturnValue(result, STRING);

    def ToString(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of ToString function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        argvalue = self.GetParamValue(params, "arg")
        result = f"{argvalue}"
        scope.SetReturnValue(result, STRING);

    def StrFormat(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of StrFormat function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = self.GetParamValue(params, "format").format(self.GetParamValue(params, "arg"))
        scope.SetReturnValue(result, STRING);

    def StrReplace(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of StrReplace function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var = self.GetParamValue(params, "_var")
        result = var.replace(self.GetParamValue(params, "from"), self.GetParamValue(params, "with"))
        scope.SetReturnValue(result, STRING);

    def StartsWith(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of StartsWith function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        haystack = self.GetParamValue(params, "haystack")
        needle = self.GetParamValue(params, "needle")
        scope.SetReturnValue(str.startswith(haystack, needle), BOOL)

    def RemoveNonAscii(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of RemoveNonAscii function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = unidecode(self.GetParamValue(params, "text"))
        scope.SetReturnValue(result, STRING)

    def ReplaceEx(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of ReplaceEx function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var  = self.GetParamValue(params, "_var")
        repl = self.GetParamValue(params, "repl")
        by   = self.GetParamValue(params, "by")
        result = var
        for ch in repl:
            result = result.replace(ch, by)
        scope.SetReturnValue(result, STRING)