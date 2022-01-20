import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.archive_record import ArchiveRecord
from ..models.dropdown_field_definition import DropdownFieldDefinition
from ..models.entity_schema_constraint import EntitySchemaConstraint
from ..models.entity_schema_containable_type import EntitySchemaContainableType
from ..models.entity_schema_type import EntitySchemaType
from ..models.float_field_definition import FloatFieldDefinition
from ..models.integer_field_definition import IntegerFieldDefinition
from ..models.schema_link_field_definition import SchemaLinkFieldDefinition
from ..models.simple_field_definition import SimpleFieldDefinition
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntitySchema")


@attr.s(auto_attribs=True, repr=False)
class EntitySchema:
    """  """

    _constraint: Union[Unset, None, EntitySchemaConstraint] = UNSET
    _containable_type: Union[Unset, EntitySchemaContainableType] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _type: Union[Unset, EntitySchemaType] = UNSET
    _prefix: Union[Unset, str] = UNSET
    _registry_id: Union[Unset, str] = UNSET
    _archive_record: Union[Unset, None, ArchiveRecord] = UNSET
    _field_definitions: Union[
        Unset,
        List[
            Union[
                SimpleFieldDefinition,
                IntegerFieldDefinition,
                FloatFieldDefinition,
                DropdownFieldDefinition,
                SchemaLinkFieldDefinition,
                UnknownType,
            ]
        ],
    ] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("constraint={}".format(repr(self._constraint)))
        fields.append("containable_type={}".format(repr(self._containable_type)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("prefix={}".format(repr(self._prefix)))
        fields.append("registry_id={}".format(repr(self._registry_id)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntitySchema({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        constraint: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._constraint, Unset):
            constraint = self._constraint.to_dict() if self._constraint else None

        containable_type: Union[Unset, int] = UNSET
        if not isinstance(self._containable_type, Unset):
            containable_type = self._containable_type.value

        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        prefix = self._prefix
        registry_id = self._registry_id
        archive_record: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._archive_record, Unset):
            archive_record = self._archive_record.to_dict() if self._archive_record else None

        field_definitions: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._field_definitions, Unset):
            field_definitions = []
            for field_definitions_item_data in self._field_definitions:
                if isinstance(field_definitions_item_data, UnknownType):
                    field_definitions_item = field_definitions_item_data.value
                elif isinstance(field_definitions_item_data, SimpleFieldDefinition):
                    field_definitions_item = field_definitions_item_data.to_dict()

                elif isinstance(field_definitions_item_data, IntegerFieldDefinition):
                    field_definitions_item = field_definitions_item_data.to_dict()

                elif isinstance(field_definitions_item_data, FloatFieldDefinition):
                    field_definitions_item = field_definitions_item_data.to_dict()

                elif isinstance(field_definitions_item_data, DropdownFieldDefinition):
                    field_definitions_item = field_definitions_item_data.to_dict()

                else:
                    field_definitions_item = field_definitions_item_data.to_dict()

                field_definitions.append(field_definitions_item)

        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if constraint is not UNSET:
            field_dict["constraint"] = constraint
        if containable_type is not UNSET:
            field_dict["containableType"] = containable_type
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if type is not UNSET:
            field_dict["type"] = type
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if registry_id is not UNSET:
            field_dict["registryId"] = registry_id
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_constraint() -> Union[Unset, None, EntitySchemaConstraint]:
            constraint = None
            _constraint = d.pop("constraint")
            if _constraint is not None and not isinstance(_constraint, Unset):
                constraint = EntitySchemaConstraint.from_dict(_constraint)

            return constraint

        constraint = (
            get_constraint() if "constraint" in d else cast(Union[Unset, None, EntitySchemaConstraint], UNSET)
        )

        def get_containable_type() -> Union[Unset, EntitySchemaContainableType]:
            containable_type = None
            _containable_type = d.pop("containableType")
            if _containable_type is not None and _containable_type is not UNSET:
                try:
                    containable_type = EntitySchemaContainableType(_containable_type)
                except ValueError:
                    containable_type = EntitySchemaContainableType.of_unknown(_containable_type)

            return containable_type

        containable_type = (
            get_containable_type()
            if "containableType" in d
            else cast(Union[Unset, EntitySchemaContainableType], UNSET)
        )

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_type() -> Union[Unset, EntitySchemaType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = EntitySchemaType(_type)
                except ValueError:
                    type = EntitySchemaType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, EntitySchemaType], UNSET)

        def get_prefix() -> Union[Unset, str]:
            prefix = d.pop("prefix")
            return prefix

        prefix = get_prefix() if "prefix" in d else cast(Union[Unset, str], UNSET)

        def get_registry_id() -> Union[Unset, str]:
            registry_id = d.pop("registryId")
            return registry_id

        registry_id = get_registry_id() if "registryId" in d else cast(Union[Unset, str], UNSET)

        def get_archive_record() -> Union[Unset, None, ArchiveRecord]:
            archive_record = None
            _archive_record = d.pop("archiveRecord")
            if _archive_record is not None and not isinstance(_archive_record, Unset):
                archive_record = ArchiveRecord.from_dict(_archive_record)

            return archive_record

        archive_record = (
            get_archive_record() if "archiveRecord" in d else cast(Union[Unset, None, ArchiveRecord], UNSET)
        )

        def get_field_definitions() -> Union[
            Unset,
            List[
                Union[
                    SimpleFieldDefinition,
                    IntegerFieldDefinition,
                    FloatFieldDefinition,
                    DropdownFieldDefinition,
                    SchemaLinkFieldDefinition,
                    UnknownType,
                ]
            ],
        ]:
            field_definitions = []
            _field_definitions = d.pop("fieldDefinitions")
            for field_definitions_item_data in _field_definitions or []:

                def _parse_field_definitions_item(
                    data: Union[Dict[str, Any]]
                ) -> Union[
                    SimpleFieldDefinition,
                    IntegerFieldDefinition,
                    FloatFieldDefinition,
                    DropdownFieldDefinition,
                    SchemaLinkFieldDefinition,
                    UnknownType,
                ]:
                    field_definitions_item: Union[
                        SimpleFieldDefinition,
                        IntegerFieldDefinition,
                        FloatFieldDefinition,
                        DropdownFieldDefinition,
                        SchemaLinkFieldDefinition,
                        UnknownType,
                    ]
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        field_definitions_item = SimpleFieldDefinition.from_dict(data)

                        return field_definitions_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        field_definitions_item = IntegerFieldDefinition.from_dict(data)

                        return field_definitions_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        field_definitions_item = FloatFieldDefinition.from_dict(data)

                        return field_definitions_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        field_definitions_item = DropdownFieldDefinition.from_dict(data)

                        return field_definitions_item
                    except:  # noqa: E722
                        pass
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        field_definitions_item = SchemaLinkFieldDefinition.from_dict(data)

                        return field_definitions_item
                    except:  # noqa: E722
                        pass
                    return UnknownType(data)

                field_definitions_item = _parse_field_definitions_item(field_definitions_item_data)

                field_definitions.append(field_definitions_item)

            return field_definitions

        field_definitions = (
            get_field_definitions()
            if "fieldDefinitions" in d
            else cast(
                Union[
                    Unset,
                    List[
                        Union[
                            SimpleFieldDefinition,
                            IntegerFieldDefinition,
                            FloatFieldDefinition,
                            DropdownFieldDefinition,
                            SchemaLinkFieldDefinition,
                            UnknownType,
                        ]
                    ],
                ],
                UNSET,
            )
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        entity_schema = cls(
            constraint=constraint,
            containable_type=containable_type,
            modified_at=modified_at,
            type=type,
            prefix=prefix,
            registry_id=registry_id,
            archive_record=archive_record,
            field_definitions=field_definitions,
            id=id,
            name=name,
        )

        entity_schema.additional_properties = d
        return entity_schema

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
    def constraint(self) -> Optional[EntitySchemaConstraint]:
        if isinstance(self._constraint, Unset):
            raise NotPresentError(self, "constraint")
        return self._constraint

    @constraint.setter
    def constraint(self, value: Optional[EntitySchemaConstraint]) -> None:
        self._constraint = value

    @constraint.deleter
    def constraint(self) -> None:
        self._constraint = UNSET

    @property
    def containable_type(self) -> EntitySchemaContainableType:
        if isinstance(self._containable_type, Unset):
            raise NotPresentError(self, "containable_type")
        return self._containable_type

    @containable_type.setter
    def containable_type(self, value: EntitySchemaContainableType) -> None:
        self._containable_type = value

    @containable_type.deleter
    def containable_type(self) -> None:
        self._containable_type = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Entity Schema was last modified """
        if isinstance(self._modified_at, Unset):
            raise NotPresentError(self, "modified_at")
        return self._modified_at

    @modified_at.setter
    def modified_at(self, value: datetime.datetime) -> None:
        self._modified_at = value

    @modified_at.deleter
    def modified_at(self) -> None:
        self._modified_at = UNSET

    @property
    def type(self) -> EntitySchemaType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: EntitySchemaType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def prefix(self) -> str:
        if isinstance(self._prefix, Unset):
            raise NotPresentError(self, "prefix")
        return self._prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        self._prefix = value

    @prefix.deleter
    def prefix(self) -> None:
        self._prefix = UNSET

    @property
    def registry_id(self) -> str:
        if isinstance(self._registry_id, Unset):
            raise NotPresentError(self, "registry_id")
        return self._registry_id

    @registry_id.setter
    def registry_id(self, value: str) -> None:
        self._registry_id = value

    @registry_id.deleter
    def registry_id(self) -> None:
        self._registry_id = UNSET

    @property
    def archive_record(self) -> Optional[ArchiveRecord]:
        if isinstance(self._archive_record, Unset):
            raise NotPresentError(self, "archive_record")
        return self._archive_record

    @archive_record.setter
    def archive_record(self, value: Optional[ArchiveRecord]) -> None:
        self._archive_record = value

    @archive_record.deleter
    def archive_record(self) -> None:
        self._archive_record = UNSET

    @property
    def field_definitions(
        self,
    ) -> List[
        Union[
            SimpleFieldDefinition,
            IntegerFieldDefinition,
            FloatFieldDefinition,
            DropdownFieldDefinition,
            SchemaLinkFieldDefinition,
            UnknownType,
        ]
    ]:
        if isinstance(self._field_definitions, Unset):
            raise NotPresentError(self, "field_definitions")
        return self._field_definitions

    @field_definitions.setter
    def field_definitions(
        self,
        value: List[
            Union[
                SimpleFieldDefinition,
                IntegerFieldDefinition,
                FloatFieldDefinition,
                DropdownFieldDefinition,
                SchemaLinkFieldDefinition,
                UnknownType,
            ]
        ],
    ) -> None:
        self._field_definitions = value

    @field_definitions.deleter
    def field_definitions(self) -> None:
        self._field_definitions = UNSET

    @property
    def id(self) -> str:
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET

    @property
    def name(self) -> str:
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
