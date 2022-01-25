class InvalidJWT(Exception):
    """Invalid JWT Token"""
    pass


class NodeUnhealthy(ConnectionError):
    """IOTA node health check returns non-200 status code"""
    pass


class NodeInternalServerError(Exception):
    """IOTA node internal error"""
    pass


class MessageNotFound(Exception):
    """Message not found"""
    pass


class UnknownError(Exception):
    """Unexpected errors"""
    pass


class SignatureKeyPairNotSet(Exception):
    """Key pair used for signature is not set"""
    pass
