"""
Exceptions to be raised when specific error occures.
"""
class InspirehepPIDDoesNotExistError(Exception):
    """Error to be raised when object does not exists.

    When trying to get some object with a unique identifier, if the object
    with the given identifier does not exists in Insiprehep database, an
    http response of 404 (Not Found) will be send to client. In such a case,
    the `InspirehepPIDDoesNotExistError` may be raised to inform the user 
    that the object does not exist and she or he can decide how to continue.
    """
    pass

class InspirehepTooManyRequestsError(Exception):
    """Error to be raised in case of Too Many requests.

    This Error must be raised when http response have status code
    of 429. The status code could be sent because of the request
    limitations of Inspirehep API.
    """
    pass