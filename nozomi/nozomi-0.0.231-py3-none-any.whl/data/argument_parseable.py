"""
Nozomi
Argument Parseable Module
author: hugh@blinkybeach.com
"""
from nozomi.data.datastore import Datastore
from typing import Optional
from nozomi.data.publicly_identified import PubliclyIdentified
from nozomi.http.parseable_data import ParseableData
from typing import Type, TypeVar

Self = TypeVar('Self', bound='ArgumentParseable')


class ArgumentParseable(PubliclyIdentified):
    """
    Protocol for types that may be retrieved via a public id supplied in
    ParseableData
    """

    @classmethod
    def assertively_from_arguments(
        Self: Type[Self],
        arguments: ParseableData,
        key: str,
        datastore: Datastore,
        in_transaction: bool = False
    ) -> Self:

        public_id = arguments.parse_string(key)

        return Self.retrieve_assertively(
            public_id=public_id,
            datastore=datastore,
            in_transaction=in_transaction
        )

    @classmethod
    def optionally_from_arguments(
        Self: Type[Self],
        arguments: ParseableData,
        key: str,
        datastore: Datastore,
        in_transaction: bool = False
    ) -> Optional[Self]:

        public_id = arguments.optionally_parse_string(key)

        if public_id is None:
            return None

        return Self.retrieve_assertively(
            public_id=public_id,
            datastore=datastore,
            in_transaction=in_transaction
        )
