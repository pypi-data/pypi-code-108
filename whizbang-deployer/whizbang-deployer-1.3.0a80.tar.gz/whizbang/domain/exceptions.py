
class WhizbangException(Exception):
    """Base class for all exceptions raised by the Whizbang domain."""
    pass

###############################################################################

class AzCliException(WhizbangException):
    pass

class AzCliRequestError(AzCliException):
    pass

class AzCliCommandParsingError(AzCliException):
    pass

class AzCliResourceDoesNotExist(AzCliException):
    pass

###############################################################################

class DeploymentTimeoutException(WhizbangException):
    pass

###############################################################################

class DatabricksException(WhizbangException):
    pass

class DatabricksJobFailure(DatabricksException):
    pass


###############################################################################

class ActiveDirectoryObjectDoesNotExist(WhizbangException):
    pass