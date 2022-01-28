"""Module to format token."""

from peachpayments_partner.exceptions import AuthError


class TokenFormatter(object):
    """A class to handle token formatting."""

    @staticmethod
    def is_valid_jwt(token: str) -> bool:
        """Checks if JWT token is valid.

        Args:
            token (str): JWT token.

        Returns:
            bool: True if JWT token is valid, False otherwise.
        """
        split_token = token.split(".")
        if len(split_token) != 3:
            return False
        for segments in split_token:
            if len(segments) < 1:
                return False
        return True

    @staticmethod
    def format(value: str) -> str:
        """Validate and format JWT token.

        Args:
            value (str): JWT token value

        Returns:
            str: formatted JWT token

        Raises:
            AuthError: if token is invalid
        """
        if not isinstance(value, str):
            raise AuthError("Invalid token type, expecting token of type str")
        token_size = value.split()
        if len(token_size) != 1:
            raise AuthError("Invalid JWT provided, expecting single JWToken")
        is_valid_token = TokenFormatter.is_valid_jwt(value)
        if not is_valid_token:
            raise AuthError("Invalid JWT format provided")
        return f"Bearer {value}"
