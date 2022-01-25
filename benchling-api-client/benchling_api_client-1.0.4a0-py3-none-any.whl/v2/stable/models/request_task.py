from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..models.schema_summary import SchemaSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequestTask")


@attr.s(auto_attribs=True, repr=False)
class RequestTask:
    """A request task."""

    _id: str
    _schema: Union[Unset, None, SchemaSummary] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _sample_group_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("schema={}".format(repr(self._schema)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("sample_group_ids={}".format(repr(self._sample_group_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "RequestTask({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._schema, Unset):
            schema = self._schema.to_dict() if self._schema else None

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        sample_group_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._sample_group_ids, Unset):
            sample_group_ids = self._sample_group_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
            }
        )
        if schema is not UNSET:
            field_dict["schema"] = schema
        if fields is not UNSET:
            field_dict["fields"] = fields
        if sample_group_ids is not UNSET:
            field_dict["sampleGroupIds"] = sample_group_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> str:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(str, UNSET)

        def get_schema() -> Union[Unset, None, SchemaSummary]:
            schema = None
            _schema = d.pop("schema")
            if _schema is not None and not isinstance(_schema, Unset):
                schema = SchemaSummary.from_dict(_schema)

            return schema

        schema = get_schema() if "schema" in d else cast(Union[Unset, None, SchemaSummary], UNSET)

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_sample_group_ids() -> Union[Unset, List[str]]:
            sample_group_ids = cast(List[str], d.pop("sampleGroupIds"))

            return sample_group_ids

        sample_group_ids = (
            get_sample_group_ids() if "sampleGroupIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        request_task = cls(
            id=id,
            schema=schema,
            fields=fields,
            sample_group_ids=sample_group_ids,
        )

        request_task.additional_properties = d
        return request_task

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

    def get(self, key, default=None) -> Optional[Any]:
        return self.additional_properties.get(key, default)

    @property
    def id(self) -> str:
        """ ID of the request task """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @property
    def schema(self) -> Optional[SchemaSummary]:
        if isinstance(self._schema, Unset):
            raise NotPresentError(self, "schema")
        return self._schema

    @schema.setter
    def schema(self, value: Optional[SchemaSummary]) -> None:
        self._schema = value

    @schema.deleter
    def schema(self) -> None:
        self._schema = UNSET

    @property
    def fields(self) -> Fields:
        if isinstance(self._fields, Unset):
            raise NotPresentError(self, "fields")
        return self._fields

    @fields.setter
    def fields(self, value: Fields) -> None:
        self._fields = value

    @fields.deleter
    def fields(self) -> None:
        self._fields = UNSET

    @property
    def sample_group_ids(self) -> List[str]:
        """ IDs of all request sample groups now associated with this task. """
        if isinstance(self._sample_group_ids, Unset):
            raise NotPresentError(self, "sample_group_ids")
        return self._sample_group_ids

    @sample_group_ids.setter
    def sample_group_ids(self, value: List[str]) -> None:
        self._sample_group_ids = value

    @sample_group_ids.deleter
    def sample_group_ids(self) -> None:
        self._sample_group_ids = UNSET
