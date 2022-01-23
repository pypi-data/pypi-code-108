"""
Nozomi
List Retrievable Module
author: hugh@blinkybeach.com
"""
from nozomi.data.publicly_identified import PubliclyIdentified
from typing import TypeVar, Type, Optional, List
from nozomi import Datastore

T = TypeVar('T', bound='ListRetrievable')


class ListRetrievable(PubliclyIdentified):

    @classmethod
    def retrieve_many(
        cls: Type[T],
        datastore: Datastore,
        public_id: str,
        in_transaction: bool = False
    ) -> List[T]:

        raise NotImplementedError

    # Override PubliclyIdentified.retrieve()
    @classmethod
    def retrieve(
        cls: Type[T],
        public_id: str,
        datastore: Datastore,
        in_transaction: bool = False
    ) -> Optional[T]:

        result = cls.retrieve_many(
            datastore=datastore,
            public_id=public_id,
            in_transaction=in_transaction
        )

        if result is None or len(result) < 1:
            return None

        return result[0]
