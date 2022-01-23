"""
Nozomi
Too Many Requests Error Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.error import NozomiError
from nozomi.http.status_code import HTTPStatusCode


class TooManyRequests(NozomiError):

    def __init__(
        self,
        client_description: str = 'You or another machine on your network has e\
ceeded request rate limits. Please slow down your requests.'
    ) -> None:

        super().__init__(
            client_description=client_description,
            http_status_code=HTTPStatusCode.TOO_MANY_REQUESTS
        )

        return
