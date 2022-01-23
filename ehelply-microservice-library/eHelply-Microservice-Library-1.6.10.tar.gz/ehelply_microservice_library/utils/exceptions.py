class PublicKeyNotFound(Exception):
    pass


class SignatureVerificationFailure(Exception):
    pass


class ExpiredToken(Exception):
    pass


class TokenNotIssuedForAudience(Exception):
    pass


class ExceptionEhelplyAuth(Exception):
    pass
