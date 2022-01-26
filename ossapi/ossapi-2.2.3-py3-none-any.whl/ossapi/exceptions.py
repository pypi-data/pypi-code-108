class InvalidURLException(Exception):
    """
    Indicates the url would not have been accepted by the api.
    Either a required parameter was missing from the url, or an invalid parameter was passed to the function.
    """
