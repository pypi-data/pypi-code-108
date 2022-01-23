"""
Nozomi
NotAuthenticated Error Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.error import NozomiError
from nozomi.http.status_code import HTTPStatusCode


class NotAuthenticated(NozomiError):

    def __init__(
        self,
        client_description: str = 'You could not be identified'
    ) -> None:

        super().__init__(
            client_description=client_description,
            http_status_code=HTTPStatusCode.NOT_AUTHENTICATED
        )

        return
