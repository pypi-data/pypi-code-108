from json import dumps
from typing import Generator, List, Union, Any, Tuple, List, TYPE_CHECKING

from .helpers import handle_and_convert_connection_errors

if TYPE_CHECKING:
    from .models import MongoModel

__all__ = ('QuerySet',)


class QuerySet(object):
    def __init__(
        self,
        model: 'MongoModel',
        data: Generator,
    ):
        self._data = data
        self._model = model

    @handle_and_convert_connection_errors
    def __iter__(self):
        for obj in self._data:
            yield self._model.parse_obj(obj)

    def __next__(self):
        return next(self.__iter__())

    @property
    def data(self) -> List:
        return [obj.data for obj in self.__iter__()]

    @property
    def generator(self) -> Generator:
        return self.__iter__()

    @property
    def data_generator(self) -> Generator:
        return (obj.data for obj in self.__iter__())

    @property
    def list(self) -> List:
        return list(self.__iter__())

    def json(self) -> str:
        return dumps(self.data)

    def first(self) -> Any:
        return next(self.__iter__())

    def serialize(
        self, fields: Union[Tuple, List], to_list: bool = True
    ) -> Union[Tuple, List]:
        return (
            [obj.serialize(fields) for obj in self.__iter__()]
            if to_list
            else tuple(obj.serialize(fields) for obj in self.__iter__())
        )

    def serialize_generator(self, fields: Union[Tuple, List]) -> Generator:
        for obj in self.__iter__():
            yield obj.serialize(fields)

    def serialize_json(self, fields: Union[Tuple, List]) -> str:
        return dumps(self.serialize(fields))
