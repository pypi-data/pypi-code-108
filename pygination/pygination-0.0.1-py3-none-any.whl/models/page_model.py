from typing import Optional,Sequence,TypeVar,Generic
from pydantic.generics import GenericModel

T = TypeVar("T")


class PageModel(GenericModel, Generic[T]):
    items: Sequence[T]
    next_page: Optional[int] = None
    previous_page: Optional[int] = None
    total: int
    pages: int

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True
