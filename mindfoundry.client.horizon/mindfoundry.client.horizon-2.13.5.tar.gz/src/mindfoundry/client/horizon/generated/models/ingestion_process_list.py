from typing import Any, Dict, List, Type, TypeVar

import attr

from ..models.ingestion_process import IngestionProcess

T = TypeVar("T", bound="IngestionProcessList")


@attr.s(auto_attribs=True)
class IngestionProcessList:
    """  """

    ingestion_processes: List[IngestionProcess]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        ingestion_processes = []
        for ingestion_processes_item_data in self.ingestion_processes:
            ingestion_processes_item = ingestion_processes_item_data.to_dict()

            ingestion_processes.append(ingestion_processes_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ingestionProcesses": ingestion_processes,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        ingestion_processes = []
        _ingestion_processes = d.pop("ingestionProcesses")
        for ingestion_processes_item_data in _ingestion_processes:
            ingestion_processes_item = IngestionProcess.from_dict(ingestion_processes_item_data)

            ingestion_processes.append(ingestion_processes_item)

        ingestion_process_list = cls(
            ingestion_processes=ingestion_processes,
        )

        ingestion_process_list.additional_properties = d
        return ingestion_process_list

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
