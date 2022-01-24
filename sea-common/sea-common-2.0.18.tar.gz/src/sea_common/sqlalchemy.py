from datetime import datetime
from math import ceil
from typing import Any, Dict, Generic, Iterator, List, Optional, Tuple, TypeVar
from dataclasses import dataclass
from base64 import b64encode, b64decode

import strawberry
from sqlalchemy import Column, DateTime, Integer, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query

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


# def sort_query(model: Any, query: Query, sort_keys: Dict[str, InstrumentedAttribute],
#                order_by: Iterator[str]) -> Query:
#     """Sort list with order_by fields, append id_ASC/id_DESC if not present."""
#     sort_list = [order.split('_') for order in order_by]
#     query = query.order_by(*[sort_keys[sort_key].desc() if sort_order == 'DESC' else sort_keys[sort_key]
#                              for (sort_key, sort_order) in sort_list if sort_key in sort_keys])
#     if not ('id_ASC' in order_by or 'id_DESC' in order_by):
#         query = query.order_by(model.id.desc() if sort_list[0][1] == 'DESC' else model.id)
#
#     return query


def sort_query(model: Any, query: Query, sort_keys: Dict[str, Any], order_by: Iterator[str]) -> Query:
    """Sort list with order_by fields, append id_ASC/id_DESC if not present."""
    sort_list = [order.split('_') for order in order_by]
    # query = query.order_by(*[sort_keys[sort_key].desc() if sort_order == 'DESC' else sort_keys[sort_key]
    #                          for (sort_key, sort_order) in sort_list if sort_key in sort_keys])
    ordering_params = []
    for sort_key, sort_order in sort_list:
        if sort_key in sort_keys:
            if sort_order == 'DESC':
                if isinstance(sort_keys[sort_key], Tuple):
                    ordering_params.append(sort_keys[sort_key][0].desc())
                    ordering_params.append(sort_keys[sort_key][1].desc())
                else:
                    ordering_params.append(sort_keys[sort_key].desc())
            else:
                if isinstance(sort_keys[sort_key], Tuple):
                    ordering_params.append(sort_keys[sort_key][0])
                    ordering_params.append(sort_keys[sort_key][1])
                else:
                    ordering_params.append(sort_keys[sort_key])

    query = query.order_by(*ordering_params)
    if not ('id_ASC' in order_by or 'id_DESC' in order_by):
        query = query.order_by(model.id.desc() if sort_list[0][1] == 'DESC' else model.id)

    return query


T = TypeVar('T')


@strawberry.type(description='A list of edges.')
class Edge(Generic[T]):
    node: T
    cursor: str


@strawberry.type(description='Information to assist with pagination.')
class PageInfo:
    start_cursor: Optional[str]
    end_cursor: Optional[str]
    has_next_page: bool
    has_previous_page: bool


class Pagination(object):
    def __init__(self, items: List[Any], page: int, per_page: int, total: int):
        self.page = page
        self.items = items
        self.prev_page = None
        self.next_page = None
        self.has_prev = page > 1
        if self.has_prev:
            self.prev_page = page - 1
        previous_items = (page - 1) * per_page
        self.has_next = previous_items + len(items) < total
        if self.has_next:
            self.next_page = page + 1
        self.total = total
        self.pages = int(ceil(total / float(per_page)))


def paginate(query: Query, page: int, per_page: int):
    if page <= 0:
        raise AttributeError('page needs to be >= 1')
    if per_page <= 0:
        raise AttributeError('per_page needs to be >= 1')
    items = query.limit(per_page).offset((page - 1) * per_page).all()
    total = query.order_by(None).count()

    return Pagination(items, page, per_page, total)


async def async_paginate(session: AsyncSession, query: Query, page: int, per_page: int):
    if page <= 0:
        raise AttributeError('page must be >= 1')
    if per_page <= 0:
        raise AttributeError('per_page must be >= 1')

    paginated_query = query.limit(per_page).offset((page - 1) * per_page)
    result = await session.execute(paginated_query)

    items = result.scalars().all()
    total = len(items)

    return Pagination(items, page, per_page, total)


@strawberry.type(description='A list of edges with pagination information.')
class Connection(Generic[T]):
    edges: List[Edge[T]]
    page_info: PageInfo
    total_count: int
    filtered_count: int
    page_count: int
    current_page: int

    @classmethod
    def load(cls, data: Pagination, counts: Tuple[int, int]):
        return Connection(
            [Edge(item, to_cursor_hash(item.created_at)) for item in data.items],
            PageInfo(
                to_cursor_hash(data.items[0].created_at) if data.items else None,
                to_cursor_hash(data.items[len(data.items) - 1].created_at) if data.items else None,
                data.has_next,
                data.has_prev,
            ),
            *counts,  # total_count and filtered_count.
            data.pages,  # page_count.
            data.page,  # current_page.
        )


def to_cursor_hash(created_at: datetime) -> str:
    return str(b64encode(str(created_at).encode('utf-8')), 'utf-8')


def from_cursor_hash(cursor: str) -> datetime:
    return datetime.fromisoformat(str(b64decode(cursor), 'utf-8'))
