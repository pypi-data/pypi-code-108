class DuplicateParameterException(Exception):
    """
    Models duplication of parameters in a definition.
    It indicates that there's an intention to define a paramter already present.
    """
    pass
