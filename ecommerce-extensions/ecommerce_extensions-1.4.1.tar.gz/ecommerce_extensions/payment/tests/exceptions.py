"""Test exceptions in order to replace ecommerce.extensions.payment.exceptions"""


class AuthorizationError(Exception):
    """This exception will replace ecommerce.extensions.payment.exceptions.AuthorizationError in tests scenarios."""


class DuplicateReferenceNumber(Exception):
    """This exception will replace ecommerce.extensions.payment.exceptions.DuplicateReferenceNumber
    in tests scenarios.
    """


class InvalidBasketError(Exception):
    """This exception will replace ecommerce.extensions.payment.exceptions.InvalidBasketError in tests scenarios."""


class InvalidSignatureError(Exception):
    """This exception will replace ecommerce.extensions.payment.exceptions.InvalidSignatureError in tests scenarios."""
