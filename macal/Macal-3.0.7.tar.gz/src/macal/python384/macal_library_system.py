#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_system.py                                                       #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 System Library                                                                        #
#                                                                                                 #
###################################################################################################

"""System library implementation"""

from .macal_library_external import *
import platform

class LibrarySystem(MacalLibrary):
    def __init__(self):
        super().__init__("system")
        self.RegisterFunction("console",          [FuncArg("arg", PARAMS)], self.console)
        self.RegisterFunction("list",             [FuncArg("arg", PARAMS)], self.create_list)
        self.RegisterFunction("record_has_field", [FuncArg("rec", RECORD), FuncArg("fieldname", STRING)], self.record_has_field)
        self.RegisterFunction("type",             [FuncArg("_var", VARIABLE)], self.Type)
        self.RegisterFunction("isString",         [FuncArg("_var", VARIABLE)], self.IsString)
        self.RegisterFunction("isInt",            [FuncArg("_var", VARIABLE)], self.IsInt)
        self.RegisterFunction("isFloat",          [FuncArg("_var", VARIABLE)], self.IsFloat)
        self.RegisterFunction("isBool",           [FuncArg("_var", VARIABLE)], self.IsBool)
        self.RegisterFunction("isRecord",         [FuncArg("_var", VARIABLE)], self.IsRecord)
        self.RegisterFunction("isArray",          [FuncArg("_var", VARIABLE)], self.IsArray)
        self.RegisterFunction("isAny",            [FuncArg("_var", VARIABLE)], self.IsAny)
        self.RegisterFunction("isParams",         [FuncArg("_var", VARIABLE)], self.IsParams)
        self.RegisterFunction("isFunction",       [FuncArg("_var", VARIABLE)], self.IsFunction)
        self.RegisterFunction("isNil",            [FuncArg("_var", VARIABLE)], self.IsNil)
        self.RegisterVariable("platform",        platform.system(), True)

    def console(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of console function"""
        self.ValidateFunction(name, func, scope)
        out_str = ""
        # Since the param is type PARAMS we can have any number of arguments, we just iterate over them.
        if len(params) > 0:
            if params[0].format:
                self.console_fmt(params)
                return
            for param in params:
                out_str = f"{out_str}{self.ParamToString(param)}"
            print(out_str)
        else:
            print()

    def console_fmt(self, args):
        """Console string formatting function"""
        fmt  = args[0].get_value()
        args = args[1:]
        if len(args) != fmt.count("{}"):
            raise RuntimeError("Number of arguments mismatch with format string.")
        argv = []
        for arg in args:
            argv.append(self.ParamToString(arg))
        print(fmt.format(*argv))

    def record_has_field(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        fieldname = self.GetParamValue(params, "fieldname")
        record = self.GetParamValue(params, "rec")
        result =  fieldname in record
        scope.SetReturnValue(result, BOOL)

    def Type(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type()
        scope.SetReturnValue(result, STRING)

    def IsString(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == STRING
        scope.SetReturnValue(result, BOOL)

    def IsInt(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == INT
        scope.SetReturnValue(result, BOOL)

    def IsFloat(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == FLOAT
        scope.SetReturnValue(result, BOOL)

    def IsBool(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == BOOL
        scope.SetReturnValue(result, BOOL)

    def IsRecord(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == RECORD
        scope.SetReturnValue(result, BOOL)

    def IsArray(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == ARRAY
        scope.SetReturnValue(result, BOOL)

    def IsAny(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == Any
        scope.SetReturnValue(result, BOOL)

    def IsParams(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == PARAMS
        scope.SetReturnValue(result, BOOL)

    def IsFunction(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == FUNCTION
        scope.SetReturnValue(result, BOOL)

    def IsNil(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of record_has_field function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        var, index = self.GetVariableFromParam(params, scope, "_var")
        if len(index) > 0:
            result = MacalScope.get_value_type(self.GetIndexedVariableValue(var, index))
        else:
            result = var.get_type() == NIL
        scope.SetReturnValue(result, BOOL)
    
    def create_list(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of console function"""
        self.ValidateFunction(name, func, scope)
        result = []
        if len(params) > 0:
            for param in params:
                result.append(param.get_value())
        else:
            raise RuntimeError("List requires at least one argument.")
        scope.SetReturnValue(result, ARRAY)
