#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_csv.py                                                          #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 CSV Library                                                                           #
#                                                                                                 #
###################################################################################################

"""CSV library implementation"""

from .macal_library_external import *

class LibraryCsv(MacalLibrary):
    def __init__(self):
        super().__init__("CSV")
        self.RegisterFunction("headersToCsv",  [FuncArg("rec", RECORD)], self.HeadersToCsv)
        self.RegisterFunction("valueToCsv",    [FuncArg("rec", RECORD)], self.ValuesToCsv)
        self.RegisterFunction("arrayToCsv",    [FuncArg("arr", ARRAY)],  self.ArrayToCsv)


    def HeadersToCsv(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of HeadersToCsv function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        rec = self.GetParamValue(params, "rec")
        result = None
        try:
            separator = '","'
            result = f'"{separator.join(rec)}"'
        except Exception as e:
            raise RuntimeError(e)
        scope.SetReturnValue(result, STRING)

    def ValuesToCsv(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of ValuesToCsv function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        rec = self.GetParamValue(params, "rec")
        result = None
        try:
            temp = []
            for fld in rec:
                temp.append('"{}"'.format(rec[fld]))
            separator = ','
            result = separator.join(temp)
        except Exception as e:
            raise RuntimeError(e)
        scope.SetReturnValue(result, STRING)

    def ArrayToCsv(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of ArrayToCsv function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        arr = self.GetParamValue(params, "arr")
        try:
            temp = []
            for fld in arr:
                temp.append('"{}"'.format(fld))
            separator = ','
            result = separator.join(temp)
        except Exception as e:
            raise RuntimeError(e)
        scope.SetReturnValue(result, STRING)
