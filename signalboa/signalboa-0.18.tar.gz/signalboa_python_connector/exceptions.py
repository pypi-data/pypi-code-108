

class InvalidApiKey(Exception):
    pass


class UnknownError(Exception):
    pass


class UnavailablePair(Exception):
    pass


class UnsupportedFrequency(Exception):
    pass


__all__ = ("InvalidApiKey",
           "UnknownError",
           "UnavailablePair",
           "UnsupportedFrequency")
