import datetime
from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr
from dateutil.parser import isoparse

from ..extensions import NotPresentError, UnknownType
from ..models.archive_record import ArchiveRecord
from ..models.assay_run_schema_automation_input_file_configs_item import (
    AssayRunSchemaAutomationInputFileConfigsItem,
)
from ..models.assay_run_schema_automation_output_file_configs_item import (
    AssayRunSchemaAutomationOutputFileConfigsItem,
)
from ..models.assay_run_schema_type import AssayRunSchemaType
from ..models.base_assay_schema_organization import BaseAssaySchemaOrganization
from ..models.dropdown_field_definition import DropdownFieldDefinition
from ..models.float_field_definition import FloatFieldDefinition
from ..models.integer_field_definition import IntegerFieldDefinition
from ..models.schema_link_field_definition import SchemaLinkFieldDefinition
from ..models.simple_field_definition import SimpleFieldDefinition
from ..types import UNSET, Unset

T = TypeVar("T", bound="AssayRunSchema")


@attr.s(auto_attribs=True, repr=False)
class AssayRunSchema:
    """  """

    _automation_input_file_configs: Union[Unset, List[AssayRunSchemaAutomationInputFileConfigsItem]] = UNSET
    _automation_output_file_configs: Union[Unset, List[AssayRunSchemaAutomationOutputFileConfigsItem]] = UNSET
    _modified_at: Union[Unset, datetime.datetime] = UNSET
    _type: Union[Unset, AssayRunSchemaType] = UNSET
    _derived_from: Union[Unset, None, str] = UNSET
    _organization: Union[Unset, BaseAssaySchemaOrganization] = UNSET
    _system_name: Union[Unset, str] = UNSET
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
        fields.append("automation_input_file_configs={}".format(repr(self._automation_input_file_configs)))
        fields.append("automation_output_file_configs={}".format(repr(self._automation_output_file_configs)))
        fields.append("modified_at={}".format(repr(self._modified_at)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("derived_from={}".format(repr(self._derived_from)))
        fields.append("organization={}".format(repr(self._organization)))
        fields.append("system_name={}".format(repr(self._system_name)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "AssayRunSchema({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        automation_input_file_configs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._automation_input_file_configs, Unset):
            automation_input_file_configs = []
            for automation_input_file_configs_item_data in self._automation_input_file_configs:
                automation_input_file_configs_item = automation_input_file_configs_item_data.to_dict()

                automation_input_file_configs.append(automation_input_file_configs_item)

        automation_output_file_configs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._automation_output_file_configs, Unset):
            automation_output_file_configs = []
            for automation_output_file_configs_item_data in self._automation_output_file_configs:
                automation_output_file_configs_item = automation_output_file_configs_item_data.to_dict()

                automation_output_file_configs.append(automation_output_file_configs_item)

        modified_at: Union[Unset, str] = UNSET
        if not isinstance(self._modified_at, Unset):
            modified_at = self._modified_at.isoformat()

        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        derived_from = self._derived_from
        organization: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._organization, Unset):
            organization = self._organization.to_dict()

        system_name = self._system_name
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
        if automation_input_file_configs is not UNSET:
            field_dict["automationInputFileConfigs"] = automation_input_file_configs
        if automation_output_file_configs is not UNSET:
            field_dict["automationOutputFileConfigs"] = automation_output_file_configs
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if type is not UNSET:
            field_dict["type"] = type
        if derived_from is not UNSET:
            field_dict["derivedFrom"] = derived_from
        if organization is not UNSET:
            field_dict["organization"] = organization
        if system_name is not UNSET:
            field_dict["systemName"] = system_name
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

        def get_automation_input_file_configs() -> Union[
            Unset, List[AssayRunSchemaAutomationInputFileConfigsItem]
        ]:
            automation_input_file_configs = []
            _automation_input_file_configs = d.pop("automationInputFileConfigs")
            for automation_input_file_configs_item_data in _automation_input_file_configs or []:
                automation_input_file_configs_item = AssayRunSchemaAutomationInputFileConfigsItem.from_dict(
                    automation_input_file_configs_item_data
                )

                automation_input_file_configs.append(automation_input_file_configs_item)

            return automation_input_file_configs

        automation_input_file_configs = (
            get_automation_input_file_configs()
            if "automationInputFileConfigs" in d
            else cast(Union[Unset, List[AssayRunSchemaAutomationInputFileConfigsItem]], UNSET)
        )

        def get_automation_output_file_configs() -> Union[
            Unset, List[AssayRunSchemaAutomationOutputFileConfigsItem]
        ]:
            automation_output_file_configs = []
            _automation_output_file_configs = d.pop("automationOutputFileConfigs")
            for automation_output_file_configs_item_data in _automation_output_file_configs or []:
                automation_output_file_configs_item = AssayRunSchemaAutomationOutputFileConfigsItem.from_dict(
                    automation_output_file_configs_item_data
                )

                automation_output_file_configs.append(automation_output_file_configs_item)

            return automation_output_file_configs

        automation_output_file_configs = (
            get_automation_output_file_configs()
            if "automationOutputFileConfigs" in d
            else cast(Union[Unset, List[AssayRunSchemaAutomationOutputFileConfigsItem]], UNSET)
        )

        def get_modified_at() -> Union[Unset, datetime.datetime]:
            modified_at: Union[Unset, datetime.datetime] = UNSET
            _modified_at = d.pop("modifiedAt")
            if _modified_at is not None and not isinstance(_modified_at, Unset):
                modified_at = isoparse(cast(str, _modified_at))

            return modified_at

        modified_at = get_modified_at() if "modifiedAt" in d else cast(Union[Unset, datetime.datetime], UNSET)

        def get_type() -> Union[Unset, AssayRunSchemaType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = AssayRunSchemaType(_type)
                except ValueError:
                    type = AssayRunSchemaType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, AssayRunSchemaType], UNSET)

        def get_derived_from() -> Union[Unset, None, str]:
            derived_from = d.pop("derivedFrom")
            return derived_from

        derived_from = get_derived_from() if "derivedFrom" in d else cast(Union[Unset, None, str], UNSET)

        def get_organization() -> Union[Unset, BaseAssaySchemaOrganization]:
            organization: Union[Unset, BaseAssaySchemaOrganization] = UNSET
            _organization = d.pop("organization")
            if not isinstance(_organization, Unset):
                organization = BaseAssaySchemaOrganization.from_dict(_organization)

            return organization

        organization = (
            get_organization()
            if "organization" in d
            else cast(Union[Unset, BaseAssaySchemaOrganization], UNSET)
        )

        def get_system_name() -> Union[Unset, str]:
            system_name = d.pop("systemName")
            return system_name

        system_name = get_system_name() if "systemName" in d else cast(Union[Unset, str], UNSET)

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

        assay_run_schema = cls(
            automation_input_file_configs=automation_input_file_configs,
            automation_output_file_configs=automation_output_file_configs,
            modified_at=modified_at,
            type=type,
            derived_from=derived_from,
            organization=organization,
            system_name=system_name,
            archive_record=archive_record,
            field_definitions=field_definitions,
            id=id,
            name=name,
        )

        assay_run_schema.additional_properties = d
        return assay_run_schema

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
    def automation_input_file_configs(self) -> List[AssayRunSchemaAutomationInputFileConfigsItem]:
        if isinstance(self._automation_input_file_configs, Unset):
            raise NotPresentError(self, "automation_input_file_configs")
        return self._automation_input_file_configs

    @automation_input_file_configs.setter
    def automation_input_file_configs(
        self, value: List[AssayRunSchemaAutomationInputFileConfigsItem]
    ) -> None:
        self._automation_input_file_configs = value

    @automation_input_file_configs.deleter
    def automation_input_file_configs(self) -> None:
        self._automation_input_file_configs = UNSET

    @property
    def automation_output_file_configs(self) -> List[AssayRunSchemaAutomationOutputFileConfigsItem]:
        if isinstance(self._automation_output_file_configs, Unset):
            raise NotPresentError(self, "automation_output_file_configs")
        return self._automation_output_file_configs

    @automation_output_file_configs.setter
    def automation_output_file_configs(
        self, value: List[AssayRunSchemaAutomationOutputFileConfigsItem]
    ) -> None:
        self._automation_output_file_configs = value

    @automation_output_file_configs.deleter
    def automation_output_file_configs(self) -> None:
        self._automation_output_file_configs = UNSET

    @property
    def modified_at(self) -> datetime.datetime:
        """ DateTime the Assay Run Schema was last modified """
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
    def type(self) -> AssayRunSchemaType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: AssayRunSchemaType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def derived_from(self) -> Optional[str]:
        if isinstance(self._derived_from, Unset):
            raise NotPresentError(self, "derived_from")
        return self._derived_from

    @derived_from.setter
    def derived_from(self, value: Optional[str]) -> None:
        self._derived_from = value

    @derived_from.deleter
    def derived_from(self) -> None:
        self._derived_from = UNSET

    @property
    def organization(self) -> BaseAssaySchemaOrganization:
        if isinstance(self._organization, Unset):
            raise NotPresentError(self, "organization")
        return self._organization

    @organization.setter
    def organization(self, value: BaseAssaySchemaOrganization) -> None:
        self._organization = value

    @organization.deleter
    def organization(self) -> None:
        self._organization = UNSET

    @property
    def system_name(self) -> str:
        if isinstance(self._system_name, Unset):
            raise NotPresentError(self, "system_name")
        return self._system_name

    @system_name.setter
    def system_name(self, value: str) -> None:
        self._system_name = value

    @system_name.deleter
    def system_name(self) -> None:
        self._system_name = UNSET

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
