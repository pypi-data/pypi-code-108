import enum
import typing

from pydantic import BaseModel, Field, create_model_from_typeddict
from pydantic.generics import GenericModel
from wisdoms_dapr.elasticsearch.searches import ESSearchResult

GenericSchema = typing.TypeVar("GenericSchema", bound=BaseModel)
PaginationResultDataType = typing.TypeVar(
    "PaginationResultDataType", bound=typing.Union[dict[str, typing.Any], BaseModel]
)

IdType = typing.TypeVar('IdType', bound=typing.Union[int, str])


class IdSchema(GenericModel, typing.Generic[IdType]):
    id: IdType


class IdsSchema(GenericModel, typing.Generic[IdType]):
    ids: list[IdType]


class PaginationResultSchema(GenericModel, typing.Generic[PaginationResultDataType]):
    """Pagination List Result Schema"""

    page: int
    size: int
    total: int
    data: typing.Optional[typing.List[PaginationResultDataType]]


class PaginationSchema(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1)

    def get_page_slice(self):
        return slice((self.page - 1) * self.size, self.page * self.size)


class PaginationSortSchema(PaginationSchema):
    sort: typing.Union[str, typing.List[str]] = ''


class ServiceRunMode(str, enum.Enum):
    """服务运行模式"""

    prod = 'prod'
    dev = 'dev'
    test = 'test'


class DaprSubscribeInfoItem(BaseModel):
    """Dapr Subscribe Item"""

    pubsubname: str
    topic: str
    route: str


ESSearchResultSchema = create_model_from_typeddict(ESSearchResult)
