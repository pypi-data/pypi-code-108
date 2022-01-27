class WhatAnimeError(Exception):
    """
    Base exception class for this module.
    """
    pass

class QuotaExceedError(WhatAnimeError):
    """
    Raises when daily quota for requests has been reached.
    """
    pass

class ImageSizeTooLargeError(WhatAnimeError):
    """
    Raises when an image uploaded was too large for the API.
    """
    pass

class APIError(WhatAnimeError):
    """
    Raises when an error occurs on the API.
    """
    pass

class InvalidToken(WhatAnimeError):
    """
    Raises when API token is invalid"""