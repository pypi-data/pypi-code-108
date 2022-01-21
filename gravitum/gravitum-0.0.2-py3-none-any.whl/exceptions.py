class IllegalIndirectionError(Exception):
    """The exception used when using virtual pointer to read or write out
    the range of bytearray.
    """
