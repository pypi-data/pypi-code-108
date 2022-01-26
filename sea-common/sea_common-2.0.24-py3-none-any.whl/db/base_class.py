from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

meta = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})
Base = declarative_base(metadata=meta)

# from typing import Any
# from sqlalchemy import inspect
# from sqlalchemy.ext.declarative import as_declarative, declared_attr
#
# @as_declarative()
# class Base:
#     id: Any
#     __name__: str
#
#     # Generate __tablename__ automatically
#     @declared_attr
#     def __tablename__(cls) -> str:
#         return cls.__name__.lower()
#
#     def to_dict(self):
#         return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
