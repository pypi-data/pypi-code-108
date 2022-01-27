from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.serialiser_name import SerialiserName
from ..models.storage_engine import StorageEngine

T = TypeVar("T", bound="StorageSpecification")


@attr.s(auto_attribs=True)
class StorageSpecification:
    """ Details on how the data is stored """

    engine: StorageEngine
    chunk_size: int
    serialiser: SerialiserName
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        engine = self.engine.value

        chunk_size = self.chunk_size
        serialiser = self.serialiser.value

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "engine": engine,
                "chunkSize": chunk_size,
                "serialiser": serialiser,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        engine = StorageEngine(d.pop("engine"))

        chunk_size = d.pop("chunkSize")

        serialiser = SerialiserName(d.pop("serialiser"))

        storage_specification = cls(
            engine=engine,
            chunk_size=chunk_size,
            serialiser=serialiser,
        )

        storage_specification.additional_properties = d
        return storage_specification

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
