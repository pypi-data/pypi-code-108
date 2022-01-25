
class UsbTmcException(Exception):
    """Generic USBTMC Exception"""
    pass
    
class UsbTmcConnectionException(UsbTmcException):
    """Exception raised in the context of a USBTMC connection"""
    pass
    
class UsbTmcStatusException(UsbTmcException):
    """Exception raised when an unexpected USBTMC error code was produced"""
    pass
    
class UsbTmcTimeoutException(UsbTmcException):
    """Exception raised when an operation timed out"""
    pass
    
class UsbTmcUnsupportedException(UsbTmcException):
    """Exception raised when an unsupported feature is requested"""
    pass
