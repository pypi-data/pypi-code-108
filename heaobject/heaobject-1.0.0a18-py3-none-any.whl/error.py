class HEAObjectException(Exception):
    """Parent exception for any exception having to do with HEA objects."""
    pass


class DeserializeException(HEAObjectException):
    """Error while deserializing a HEA object."""
    pass

