from typing import List, Union, Tuple

from eyja.utils import now
from eyja.hubs import DataHub
from eyja.errors import ParseModelNamespaceError

from .base_data_model import BaseDataModel
from .data_filter import DataFilter


class BaseStorageModel(BaseDataModel):
    _namespace: str = None
    _indexes: List[str] = [
        'created_at',
        'updated_at',
    ]
    _expiration = 0
    _key_template = 'object_id'
    _hidden_fields = []
    _update_fields = []

    def __init__(self, **data):
        if 'object_id' not in data:
            data.setdefault('object_id', None)
            data.setdefault('created_at', now())
        data.setdefault('updated_at', now())
        super().__init__(**data)

    @classmethod
    def namespace(self) -> Tuple[str, str, str, str]:
        namespaces = str(self._namespace).split(':')
        if len(namespaces) != 4:
            raise ParseModelNamespaceError(
                'A namespace must have four parts - storage type, storage connection, objectspace, and object type - separated by ":"'
            )

        return tuple(namespaces)

    async def save(self) -> None:
        self.updated_at = now()
        await DataHub.save(self)

    async def delete(self) -> None:
        await DataHub.delete(self)

    def update(self, data: dict) -> None:
        for field_key, field_value in data.items():
            if field_key in self._update_fields:
                setattr(self, field_key, field_value)

    @property
    def data(self):
        obj_data = self.dict()

        return obj_data

    @property
    def cleared_data(self):
        obj_data = self.data
        for field in self._hidden_fields:
            obj_data.pop(field)

        return obj_data

    @classmethod
    async def delete_all(cls, filter: dict) -> None:
        await DataHub.delete_all(cls, filter)

    @classmethod
    async def get(cls, object_id: str) -> 'BaseStorageModel':
        return await DataHub.get(cls, object_id)

    @classmethod
    async def find(cls, filter: Union[DataFilter,dict]) -> List['BaseStorageModel']:
        if isinstance(filter, dict):
            filter = DataFilter(fields=filter)

        return await DataHub.find(cls, filter)

    @classmethod
    async def count(cls, filter: dict) -> int:
        d_filter = DataFilter(fields=filter)

        return await DataHub.count(cls, d_filter)
