#-------------------------------------------------------------------------------------------------#
# Filename:       | macal_library_syslog.py                                                       #
# Author:         | Marco Caspers                                                                 #
# Description:    |                                                                               #
#-------------------------------------------------------------------------------------------------#
#                                                                                                 #
# Macal 2.0 Syslog Library                                                                        #
#                                                                                                 #
###################################################################################################

"""Syslog library implementation"""

from .macal_library_external import *
from .macal_SysLog_class import SysLog

class LibrarySyslog(MacalLibrary):
    def __init__(self):
        super().__init__("syslog")
        self.RegisterFunction("syslog",             [FuncArg("level", STRING),   FuncArg("message", STRING)], self.Syslog)
        self.RegisterFunction("syslog_init",        [FuncArg("remote", BOOL)], self.SyslogInit)
        self.RegisterFunction("syslog_set_address", [FuncArg("address", STRING), FuncArg("port", INT)], self.SyslogSetAddress)
        self.SysLog = SysLog()
        
    def Syslog(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of Syslog function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        level = self.GetParamValue(params, "level")
        message = self.GetParamValue(params, "message")
        if level == "debug":
            self.SysLog.debug(message)
        elif level == "info" or level == "information":
            self.SysLog.info(message)
        elif level == "warn" or level == "warning":
            self.SysLog.warn(message)
        elif level == "error":
            self.SysLog.error(message)
        elif level == "critical":
            self.SysLog.critical(message)
        else:
            raise Exception(f"Invalid syslog level given: {level}")

    def SyslogInit(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of SysLog init function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        remote = self.GetParamValue(params, "remote")
        self.SysLog.SysLogInit(remote)

    def SyslogSetAddress(self, func: MacalFunction, name: str, params: list, scope: MacalScope):
        """Implementation of SysLog SetAddress function"""
        self.ValidateFunction(name, func, scope)
        self.ValidateParams(name, params, scope, func)
        address = self.GetParamValue(params, "address")
        port = self.GetParamValue(params, "port")
        self.SysLog.SysLogSetAddress(address, port)