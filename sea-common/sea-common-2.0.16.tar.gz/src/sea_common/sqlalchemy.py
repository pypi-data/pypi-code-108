from datetime import datetime
from typing import Any, Dict, Iterator, Optional
from dataclasses import dataclass

from sqlalchemy import Column, DateTime, Integer, Table
from sqlalchemy.orm import InstrumentedAttribute, Query

from .db import AsyncSessionLocal


@dataclass(init=False)
class CreateUpdateFields:
    # Keep track when records are created and updated.
    created_at: Optional[datetime] = Column(DateTime(), index=True, default=datetime.utcnow)
    updated_at: Optional[datetime] = Column(DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: Optional[int] = Column(Integer, default=1)
    updated_by: Optional[int] = Column(Integer)


class ResourceMixin(CreateUpdateFields):
    __table__: Table

    async def async_save(self):
        async with AsyncSessionLocal() as session:
            session.add(self)
            await session.commit()


class ResourceMixinWithVersion(ResourceMixin):
    version: Optional[int] = Column(Integer, nullable=False)
    __mapper_args__ = {'version_id_col': version}


# @dataclass(init=False)
# class RefSeqFields:
#     id: strawberry.ID = Column(String(24), primary_key=True)  # RefSeq acc version, e.g. NM_003331.5 / NP_003322.3.
#     acc: str = Column(String(16), unique=True, index=True, nullable=False)


# class RefseqMixin(RefSeqFields):
#     query: BaseQuery
#
#     @classmethod
#     def find_by_refseq_id(cls, refseq_id: str):
#         """Find a model by its RefSeq accession ID."""
#         return cls.query.filter((cls.id == refseq_id) | (cls.acc == refseq_id)).first()


# class ExternalResourceMixin:
#     __table__: Table
#     query: BaseQuery
#
#     # Keep track when records are created and updated.
#     created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
#     updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
#     created_by = db.Column(db.Integer, default=1)
#     updated_by = db.Column(db.Integer)
#
#     @classmethod
#     def get_by_id(cls, id: Union[int, str, List[str]]):
#         try:
#             return cls.query.get(id)
#         except ValueError:
#             return None


def sort_query(model: Any, query: Query, sort_keys: Dict[str, InstrumentedAttribute],
               order_by: Iterator[str]) -> Query:
    """Sort list with order_by fields, append id_ASC/id_DESC if not present."""
    sort_list = [order.split('_') for order in order_by]
    query = query.order_by(*[sort_keys[sort_key].desc() if sort_order == 'DESC' else sort_keys[sort_key]
                             for (sort_key, sort_order) in sort_list if sort_key in sort_keys])
    if not ('id_ASC' in order_by or 'id_DESC' in order_by):
        query = query.order_by(model.id.desc() if sort_list[0][1] == 'DESC' else model.id)

    return query
