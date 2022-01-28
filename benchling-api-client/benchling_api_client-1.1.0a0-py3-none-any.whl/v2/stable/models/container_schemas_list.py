from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.container_schema import ContainerSchema
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContainerSchemasList")


@attr.s(auto_attribs=True, repr=False)
class ContainerSchemasList:
    """  """

    _container_schemas: Union[Unset, List[ContainerSchema]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("container_schemas={}".format(repr(self._container_schemas)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "ContainerSchemasList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        container_schemas: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._container_schemas, Unset):
            container_schemas = []
            for container_schemas_item_data in self._container_schemas:
                container_schemas_item = container_schemas_item_data.to_dict()

                container_schemas.append(container_schemas_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if container_schemas is not UNSET:
            field_dict["containerSchemas"] = container_schemas

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_container_schemas() -> Union[Unset, List[ContainerSchema]]:
            container_schemas = []
            _container_schemas = d.pop("containerSchemas")
            for container_schemas_item_data in _container_schemas or []:
                container_schemas_item = ContainerSchema.from_dict(container_schemas_item_data)

                container_schemas.append(container_schemas_item)

            return container_schemas

        container_schemas = (
            get_container_schemas()
            if "containerSchemas" in d
            else cast(Union[Unset, List[ContainerSchema]], UNSET)
        )

        container_schemas_list = cls(
            container_schemas=container_schemas,
        )

        container_schemas_list.additional_properties = d
        return container_schemas_list

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
    def container_schemas(self) -> List[ContainerSchema]:
        if isinstance(self._container_schemas, Unset):
            raise NotPresentError(self, "container_schemas")
        return self._container_schemas

    @container_schemas.setter
    def container_schemas(self, value: List[ContainerSchema]) -> None:
        self._container_schemas = value

    @container_schemas.deleter
    def container_schemas(self) -> None:
        self._container_schemas = UNSET
