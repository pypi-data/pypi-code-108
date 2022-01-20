import datetime
from typing import Any, Dict, List, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..models.raw_column import RawColumn
from ..models.storage_specification import StorageSpecification
from ..types import UNSET, Unset

T = TypeVar("T", bound="Dataset")


@attr.s(auto_attribs=True)
class Dataset:
    """  """

    name: str
    id: int
    columns: List[RawColumn]
    n_rows: int
    n_columns: int
    upload_date: datetime.datetime
    upload_user_id: int
    time_index: str
    is_time_index_generated: bool
    storage_specification: StorageSpecification
    source_file_bytes: int
    last_update_date: Union[Unset, None, datetime.datetime] = UNSET
    last_update_error: Union[Unset, None, str] = UNSET
    description: Union[Unset, str] = "Description unspecified"
    storage_size_bytes: Union[Unset, int] = 0
    first_index_timestamp: Union[Unset, None, int] = UNSET
    last_index_timestamp: Union[Unset, None, int] = UNSET
    indices_unique: Union[Unset, bool] = False
    cadence: Union[Unset, None, float] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        name = self.name
        id = self.id
        columns = []
        for columns_item_data in self.columns:
            columns_item = columns_item_data.to_dict()

            columns.append(columns_item)

        n_rows = self.n_rows
        n_columns = self.n_columns
        upload_date = self.upload_date.isoformat()

        upload_user_id = self.upload_user_id
        time_index = self.time_index
        is_time_index_generated = self.is_time_index_generated
        storage_specification = self.storage_specification.to_dict()

        source_file_bytes = self.source_file_bytes
        last_update_date: Union[Unset, None, str] = UNSET
        if not isinstance(self.last_update_date, Unset):
            last_update_date = self.last_update_date.isoformat() if self.last_update_date else None

        last_update_error = self.last_update_error
        description = self.description
        storage_size_bytes = self.storage_size_bytes
        first_index_timestamp = self.first_index_timestamp
        last_index_timestamp = self.last_index_timestamp
        indices_unique = self.indices_unique
        cadence = self.cadence

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "id": id,
                "columns": columns,
                "nRows": n_rows,
                "nColumns": n_columns,
                "uploadDate": upload_date,
                "uploadUserId": upload_user_id,
                "timeIndex": time_index,
                "isTimeIndexGenerated": is_time_index_generated,
                "storageSpecification": storage_specification,
                "sourceFileBytes": source_file_bytes,
            }
        )
        if last_update_date is not UNSET:
            field_dict["lastUpdateDate"] = last_update_date
        if last_update_error is not UNSET:
            field_dict["lastUpdateError"] = last_update_error
        if description is not UNSET:
            field_dict["description"] = description
        if storage_size_bytes is not UNSET:
            field_dict["storageSizeBytes"] = storage_size_bytes
        if first_index_timestamp is not UNSET:
            field_dict["firstIndexTimestamp"] = first_index_timestamp
        if last_index_timestamp is not UNSET:
            field_dict["lastIndexTimestamp"] = last_index_timestamp
        if indices_unique is not UNSET:
            field_dict["indicesUnique"] = indices_unique
        if cadence is not UNSET:
            field_dict["cadence"] = cadence

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        name = d.pop("name")

        id = d.pop("id")

        columns = []
        _columns = d.pop("columns")
        for columns_item_data in _columns:
            columns_item = RawColumn.from_dict(columns_item_data)

            columns.append(columns_item)

        n_rows = d.pop("nRows")

        n_columns = d.pop("nColumns")

        upload_date = isoparse(d.pop("uploadDate"))

        upload_user_id = d.pop("uploadUserId")

        time_index = d.pop("timeIndex")

        is_time_index_generated = d.pop("isTimeIndexGenerated")

        storage_specification = StorageSpecification.from_dict(d.pop("storageSpecification"))

        source_file_bytes = d.pop("sourceFileBytes")

        _last_update_date = d.pop("lastUpdateDate", UNSET)
        last_update_date: Union[Unset, None, datetime.datetime]
        if _last_update_date is None:
            last_update_date = None
        elif isinstance(_last_update_date, Unset):
            last_update_date = UNSET
        else:
            last_update_date = isoparse(_last_update_date)

        last_update_error = d.pop("lastUpdateError", UNSET)

        description = d.pop("description", UNSET)

        storage_size_bytes = d.pop("storageSizeBytes", UNSET)

        first_index_timestamp = d.pop("firstIndexTimestamp", UNSET)

        last_index_timestamp = d.pop("lastIndexTimestamp", UNSET)

        indices_unique = d.pop("indicesUnique", UNSET)

        cadence = d.pop("cadence", UNSET)

        dataset = cls(
            name=name,
            id=id,
            columns=columns,
            n_rows=n_rows,
            n_columns=n_columns,
            upload_date=upload_date,
            upload_user_id=upload_user_id,
            time_index=time_index,
            is_time_index_generated=is_time_index_generated,
            storage_specification=storage_specification,
            source_file_bytes=source_file_bytes,
            last_update_date=last_update_date,
            last_update_error=last_update_error,
            description=description,
            storage_size_bytes=storage_size_bytes,
            first_index_timestamp=first_index_timestamp,
            last_index_timestamp=last_index_timestamp,
            indices_unique=indices_unique,
            cadence=cadence,
        )

        dataset.additional_properties = d
        return dataset

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
