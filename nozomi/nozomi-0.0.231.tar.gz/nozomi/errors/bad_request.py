"""
Nozomi
Bad Request Error Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.error import NozomiError
from nozomi.http.status_code import HTTPStatusCode


class BadRequest(NozomiError):

    def __init__(
        self,
        client_description: str = 'We could not understand the data received'
    ) -> None:

        super().__init__(
            client_description=client_description,
            http_status_code=HTTPStatusCode.BAD_REQUEST
        )

        return
