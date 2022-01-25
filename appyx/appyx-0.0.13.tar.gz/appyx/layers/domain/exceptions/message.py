class MessageMissingArgumentsException(Exception):
    """
    This object models a lack of required arguments in a message.
    """
    pass


class MessageWithInvalidArgumentsException(Exception):
    """
    This object models a use of invalid arguments in a message.
    """
    pass
