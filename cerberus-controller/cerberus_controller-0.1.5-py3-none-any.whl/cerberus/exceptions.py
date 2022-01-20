""" Cerberus exceptions """

class ConfigError(Exception):
    """ Exception for malformed configs """
    pass

class EmptyConfigError(Exception):
    """ Empty config error """
    pass