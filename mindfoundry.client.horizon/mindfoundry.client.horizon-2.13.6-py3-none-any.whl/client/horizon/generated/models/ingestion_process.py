import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.ingestion_status import IngestionStatus
from ..types import UNSET, Unset

T = TypeVar("T", bound="IngestionProcess")


@attr.s(auto_attribs=True)
class IngestionProcess:
    """ An asynchronous process which parses, validates and profiles datasets on upload """

    id: int
    status: IngestionStatus
    upload_size_bytes: int
    dataset_name: str
    creation_user_id: int
    creation_date: datetime.datetime
    last_update_error: Union[Unset, None, str] = UNSET
    error: Union[Unset, None, str] = UNSET
    task_id: Union[Unset, None, str] = UNSET
    dataset_id: Union[Unset, None, int] = UNSET
    last_update_date: Union[Unset, None, datetime.datetime] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        id = self.id
        status = self.status.value

        upload_size_bytes = self.upload_size_bytes
        dataset_name = self.dataset_name
        creation_user_id = self.creation_user_id
        creation_date = self.creation_date.isoformat()

        last_update_error = self.last_update_error
        error = self.error
        task_id = self.task_id
        dataset_id = self.dataset_id
        last_update_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.last_update_date, Unset):
            last_update_date = self.last_update_date.isoformat() if self.last_update_date else None

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "uploadSizeBytes": upload_size_bytes,
                "datasetName": dataset_name,
                "creationUserId": creation_user_id,
                "creationDate": creation_date,
            }
        )
        if last_update_error is not UNSET:
            field_dict["lastUpdateError"] = last_update_error
        if error is not UNSET:
            field_dict["error"] = error
        if task_id is not UNSET:
            field_dict["taskId"] = task_id
        if dataset_id is not UNSET:
            field_dict["datasetId"] = dataset_id
        if last_update_date is not UNSET:
            field_dict["lastUpdateDate"] = last_update_date

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        id = d.pop("id")

        status = IngestionStatus(d.pop("status"))

        upload_size_bytes = d.pop("uploadSizeBytes")

        dataset_name = d.pop("datasetName")

        creation_user_id = d.pop("creationUserId")

        creation_date = isoparse(d.pop("creationDate"))

        last_update_error = d.pop("lastUpdateError", UNSET)

        error = d.pop("error", UNSET)

        task_id = d.pop("taskId", UNSET)

        dataset_id = d.pop("datasetId", UNSET)

        _last_update_date = d.pop("lastUpdateDate", UNSET)
        last_update_date: Union[Unset, None, datetime.datetime]
        if _last_update_date is None:
            last_update_date = None
        elif isinstance(_last_update_date, Unset):
            last_update_date = UNSET
        else:
            last_update_date = isoparse(_last_update_date)

        ingestion_process = cls(
            id=id,
            status=status,
            upload_size_bytes=upload_size_bytes,
            dataset_name=dataset_name,
            creation_user_id=creation_user_id,
            creation_date=creation_date,
            last_update_error=last_update_error,
            error=error,
            task_id=task_id,
            dataset_id=dataset_id,
            last_update_date=last_update_date,
        )

        ingestion_process.additional_properties = d
        return ingestion_process

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
