"""
Nozomi
Already Exists Error Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.error import NozomiError
from nozomi.http.status_code import HTTPStatusCode


class AlreadyExists(NozomiError):

    def __init__(
        self,
        client_description: str = 'The specified record already exists'
    ) -> None:

        super().__init__(
            client_description=client_description,
            http_status_code=HTTPStatusCode.ALREADY_EXISTS
        )

        return
