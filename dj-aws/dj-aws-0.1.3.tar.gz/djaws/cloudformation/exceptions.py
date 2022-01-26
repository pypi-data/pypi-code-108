from djaws.exceptions import AWSError


class CFError(AWSError):
    """All Cloud Formation Exceptions in the AWS App inherit from this class"""


class CFClientError(CFError):
    """All Cloud Formation Exceptions in the AWS App inherit from this class"""
