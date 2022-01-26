#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_time.py                                                         #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Time Library                                                                          #
#                                                                                                 #
###################################################################################################

"""Time library implementation"""
from datetime import datetime
import time

from .macal_library_external import *

class LibraryTime(MacalLibrary):
    def __init__(self):
        super().__init__("time")
        self.RegisterFunction("date_to_unix",   [FuncArg("date_str", STRING)], self.DateToUnix)
        self.RegisterFunction("iso_to_unix",    [FuncArg("date_str", STRING)], self.IsoToUnix)
        self.RegisterFunction("date_from_unix", [FuncArg("seconds", INT)], self.DateFromUnix)
        self.RegisterFunction("iso_from_unix",  [FuncArg("seconds", INT)], self.IsoFromUnix)
        self.RegisterFunction("utcnow",         [], self.UtcNow)
        self.RegisterFunction("utcisonow",      [], self.UtcIsoNow)
        self.RegisterFunction("isonow",         [], self.IsoNow)
        self.RegisterFunction("now",            [], self.Now)
        self.RegisterFunction("perf_counter",   [], self.PerfCounter)
        self.NUM_SECONDS_FIVE_MINUTES = 300
        self.NUM_SECONDS_ONE_HOUR = 3600
        self.TIME_FORMAT = '%Y%m%d%H%M%S'
        self.ISO_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"
        self.ISO_TIME_tzFORMAT = "%Y-%m-%dT%H:%M:%S.0Z"
        self.__stopwatch__ = 0

    def DateToUnix(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Convert a date_string of format YYYYMMDDhhmmss to unix time integer.
           Assumes the date string object is UTC time."""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        dt = datetime.strptime(self.GetParamValue(params, "date_str"), self.TIME_FORMAT)
        epoch = datetime(1970, 1, 1)
        result = int((dt - epoch).total_seconds())
        scope.SetReturnValue(result, INT)

    def IsoToUnix(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Convert a date_string of format %Y-%m-%dT%H:%M:%S.%f to unix time integer.
           Assumes the date string object is in iso format."""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        dt = datetime.strptime(self.GetParamValue(params, "date_str"), self.ISO_TIME_FORMAT)
        epoch = datetime(1970, 1, 1)
        result = int((dt - epoch).total_seconds())
        scope.SetReturnValue(result, INT)

    def DateFromUnix(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Converts time in seconds since UNIX EPOCH to UTC Time format"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = time.strftime(self.TIME_FORMAT, time.gmtime(self.GetParamValue(params, "seconds")))
        scope.SetReturnValue(result, STRING)

    def IsoFromUnix(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Converts time in seconds since UNIX EPOCH to UTC Time format"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        result = time.strftime(self.ISO_TIME_tzFORMAT, time.gmtime(self.GetParamValue(params, "seconds")))
        scope.SetReturnValue(result, STRING)

    def UtcNow(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        self.ValidateFunction(name, func, scope)
        result = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        scope.SetReturnValue(result, STRING)

    def UtcIsoNow(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        self.ValidateFunction(name, func, scope)
        result = "{}Z".format(datetime.utcnow().isoformat())
        scope.SetReturnValue(result, STRING)

    def IsoNow(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        self.ValidateFunction(name, func, scope)
        result = datetime.now().isoformat()
        scope.SetReturnValue(result, STRING)

    def Now(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        self.ValidateFunction(name, func, scope)
        result = datetime.now().strftime("%Y%m%d%H%M%S")
        scope.SetReturnValue(result, STRING)

    def PerfCounter(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        self.ValidateFunction(name, func, scope)
        result = time.perf_counter()
        scope.SetReturnValue(result, FLOAT)
