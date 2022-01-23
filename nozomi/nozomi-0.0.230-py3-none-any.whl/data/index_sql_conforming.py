"""
Nozomi
Index SQL Conforming Protocol Module
author: hugh@blinkybeach.com
"""
from nozomi.data.sql_conforming import SQLConforming
from nozomi.ancillary.immutable import Immutable


class IndexSQLConforming(SQLConforming):
    """
    Abstract class defining an interface for classes whose SQL representation
    is their integer datastore indexid.
    """

    indexid: int = NotImplemented

    sql_representation = Immutable(lambda s: s._form_index_sql_representation())

    def _form_index_sql_representation(self) -> bytes:
        if not isinstance(self.indexid, int):
            raise NotImplementedError('Implement integer .indexid')
        return self.adapt_integer(self.indexid)
