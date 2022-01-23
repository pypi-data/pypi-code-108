from enum import Enum


class ExitCodeEnum(Enum):
    """ A number of exit codes have special meanings,and should be
    avoided. See: https://tldp.org/LDP/abs/html/exitcodes.html """
    SUCCESS = 0
    UNSPECIFIED_FAILURE = 1
    REGISTRY_NAME_COLLISION = 3


DEFAULT_REGISTRY_NAME = 'default'
