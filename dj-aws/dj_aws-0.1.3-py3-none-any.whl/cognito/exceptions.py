from djaws.exceptions import AWSError


class CognitoError(AWSError):
    """All Cognito Exceptions in the AWS App inherit from this class"""


class CognitoClientError(CognitoError):
    """All Cognito Exceptions in the AWS App inherit from this class"""


class CognitoUserNotFoundError(CognitoClientError):
    """Cognito User not found"""


class CognitoUserNotAuthorizedError(CognitoClientError):
    """Cognito User not authorized"""


class CognitoUserNotConfirmedError(CognitoClientError):
    """Cognito User not confirmed """


class CognitoUserPasswordValidationError(CognitoClientError):
    """Cognito User password failed validation """


class CognitoUsernameExistsError(CognitoClientError):
    """Cognito User username already exists """
