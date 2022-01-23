"""
Nozomi
NotAuthorised Error Module
author: hugh@blinkybeach.com
"""
from nozomi.errors.error import NozomiError
from nozomi.http.status_code import HTTPStatusCode
from typing import TypeVar, Type, Union, Optional
from nozomi.data.named import Named

T = TypeVar('T', bound='NotFound')


class NotFound(NozomiError):

    def __init__(
        self,
        client_description: str = 'A requested resource could not be found'
    ) -> None:

        super().__init__(
            client_description=client_description,
            http_status_code=HTTPStatusCode.NOT_FOUND
        )

        return

    @classmethod
    def for_object(
        cls: Type[T],
        name: Union[str, Named, Type[Named]],
        id_: Optional[str] = None
    ) -> T:

        derived_name = name if isinstance(name, str) else name.name

        if id_ is not None:
            raise Warning('id_ parameter deprecated')

        return cls(
            client_description='No {n} found with the supplied ID'.format(
                n=str(derived_name)
            )
        )
