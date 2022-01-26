from typing import Optional, Dict

class RequirementError(BaseException):
	pass

class NamespaceNotFound(BaseException):
	pass

class NamespaceError(BaseException):
	pass

class UnsupportedHardware(BaseException):
	pass

class InterfaceNotFound(BaseException):
	pass

class InterfaceError(BaseException):
	pass

class ResourceNotFound(BaseException):
	pass

class ResourceError(BaseException):
	pass

class ConfigurationError(BaseException):
	pass

class QMPError(BaseException):
	def __init__(self, error_obj :Dict[str, str]) -> None:
		self.type = error_obj.get('class')
		self.message = error_obj.get('desc')

class SysCallError(BaseException):
	def __init__(self, message :str, exit_code :Optional[int]) -> None:
		super(SysCallError, self).__init__(message)
		self.message = message
		self.exit_code = exit_code