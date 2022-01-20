import re
from typing import Generic, Optional, TypeVar

import fastapi
import pydantic
import pydantic.generics
import ujson

snake_regexp = re.compile(r'_([a-z])')


class Model(pydantic.BaseModel):
    class Config:
        allow_population_by_field_name = True
        json_loads = ujson.loads
        json_dumps = ujson.dumps

        @classmethod
        def alias_generator(cls, field: str):
            if field == 'id_':
                return 'id'
            return re.sub(snake_regexp, lambda match: match[1].upper(), field)


class FrozenModel(Model):
    class Config(Model.Config):
        allow_mutation = False


T = TypeVar('T', bound=Model)


class Details(FrozenModel):
    last_id: Optional[int] = None
    total_pages: Optional[int] = None
    info: Optional[str] = None
    total_left: Optional[int] = None


class BaseResponse(pydantic.generics.GenericModel, Generic[T]):
    data: list[T]
    details: Optional[Details] = pydantic.Field(default_factory=Details)


class Page(FrozenModel):
    last_id: int = fastapi.Query(0, ge=0)
    per_page: int = fastapi.Query(20, ge=5, le=100)


class BaseError(Model):
    title: str
    path: str
    status: int
    detail: str
