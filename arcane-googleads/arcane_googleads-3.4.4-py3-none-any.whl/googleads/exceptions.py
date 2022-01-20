class GoogleAdsAccountNoAccessException(Exception):
    """ Raised when we cannot access to an account """
    pass

class GoogleAdsAccountException(Exception):
    """ Raised when a google ads error has occured expect user permission denied"""
    pass

class EmptyCredentialsError(Exception):
    """ Raised when empty credentials are provided"""
    pass
