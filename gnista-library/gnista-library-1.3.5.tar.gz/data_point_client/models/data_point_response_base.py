import datetime
from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr
from dateutil.parser import isoparse

from ..models.data_bucket_base import DataBucketBase
from ..models.data_point_origin import DataPointOrigin
from ..models.en_data_point_existence_dto import EnDataPointExistenceDTO
from ..models.en_data_point_state_dto import EnDataPointStateDTO
from ..types import UNSET, Unset

T = TypeVar("T", bound="DataPointResponseBase")


@attr.s(auto_attribs=True)
class DataPointResponseBase:
    """ """

    data_point_id: str
    created_on: datetime.datetime
    name: Union[Unset, None, str] = UNSET
    description: Union[Unset, None, str] = UNSET
    created_by: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    store: Union[Unset, None, DataBucketBase] = UNSET
    state: Union[Unset, EnDataPointStateDTO] = UNSET
    existence: Union[Unset, EnDataPointExistenceDTO] = UNSET
    error_details: Union[Unset, None, str] = UNSET
    origin: Union[Unset, None, DataPointOrigin] = UNSET
    used_in_calculations: Union[Unset, None, List[str]] = UNSET

    def to_dict(self) -> Dict[str, Any]:
        data_point_id = self.data_point_id
        created_on = self.created_on.isoformat()

        name = self.name
        description = self.description
        created_by = self.created_by
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        store: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.store, Unset):
            store = self.store.to_dict() if self.store else None

        state: Union[Unset, str] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        existence: Union[Unset, str] = UNSET
        if not isinstance(self.existence, Unset):
            existence = self.existence.value

        error_details = self.error_details
        origin: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self.origin, Unset):
            origin = self.origin.to_dict() if self.origin else None

        used_in_calculations: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.used_in_calculations, Unset):
            if self.used_in_calculations is None:
                used_in_calculations = None
            else:
                used_in_calculations = self.used_in_calculations

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "dataPointId": data_point_id,
                "createdOn": created_on,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if tags is not UNSET:
            field_dict["tags"] = tags
        if store is not UNSET:
            field_dict["store"] = store
        if state is not UNSET:
            field_dict["state"] = state
        if existence is not UNSET:
            field_dict["existence"] = existence
        if error_details is not UNSET:
            field_dict["errorDetails"] = error_details
        if origin is not UNSET:
            field_dict["origin"] = origin
        if used_in_calculations is not UNSET:
            field_dict["usedInCalculations"] = used_in_calculations

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        data_point_id = d.pop("dataPointId")

        created_on = isoparse(d.pop("createdOn"))

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        created_by = d.pop("createdBy", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        _store = d.pop("store", UNSET)
        store: Union[Unset, None, DataBucketBase]
        if _store is None:
            store = None
        elif isinstance(_store, Unset):
            store = UNSET
        else:
            store = DataBucketBase.from_dict(_store)

        _state = d.pop("state", UNSET)
        state: Union[Unset, EnDataPointStateDTO]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = EnDataPointStateDTO(_state)

        _existence = d.pop("existence", UNSET)
        existence: Union[Unset, EnDataPointExistenceDTO]
        if isinstance(_existence, Unset):
            existence = UNSET
        else:
            existence = EnDataPointExistenceDTO(_existence)

        error_details = d.pop("errorDetails", UNSET)

        _origin = d.pop("origin", UNSET)
        origin: Union[Unset, None, DataPointOrigin]
        if _origin is None:
            origin = None
        elif isinstance(_origin, Unset):
            origin = UNSET
        else:
            origin = DataPointOrigin.from_dict(_origin)

        used_in_calculations = cast(List[str], d.pop("usedInCalculations", UNSET))

        data_point_response_base = cls(
            data_point_id=data_point_id,
            created_on=created_on,
            name=name,
            description=description,
            created_by=created_by,
            tags=tags,
            store=store,
            state=state,
            existence=existence,
            error_details=error_details,
            origin=origin,
            used_in_calculations=used_in_calculations,
        )

        return data_point_response_base
