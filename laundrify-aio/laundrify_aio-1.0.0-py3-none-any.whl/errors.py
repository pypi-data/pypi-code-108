"""laundrify API errors"""

class LaundrifyApiException(Exception):
	"""Base exception for laundrify_aio"""

class InvalidFormat(LaundrifyApiException):
	"""AuthCode has an invalid format."""

class UnknownAuthCode(LaundrifyApiException):
	"""AuthCode could not be found."""

class ApiConnectionError(LaundrifyApiException):
	"""Could not connect the the API"""

class ApiUnauthorized(LaundrifyApiException):
	"""Request is not authorized."""
