from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError, UnknownType
from ..models.archive_record import ArchiveRecord
from ..models.dropdown_field_definition import DropdownFieldDefinition
from ..models.float_field_definition import FloatFieldDefinition
from ..models.integer_field_definition import IntegerFieldDefinition
from ..models.schema_link_field_definition import SchemaLinkFieldDefinition
from ..models.simple_field_definition import SimpleFieldDefinition
from ..models.team_summary import TeamSummary
from ..models.workflow_output_schema import WorkflowOutputSchema
from ..models.workflow_task_schema_execution_type import WorkflowTaskSchemaExecutionType
from ..models.workflow_task_status_lifecycle import WorkflowTaskStatusLifecycle
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskSchema")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskSchema:
    """  """

    _can_set_assignee_on_task_creation: Union[Unset, bool] = UNSET
    _default_creation_folder_id: Union[Unset, None, str] = UNSET
    _default_entry_execution_folder_id: Union[Unset, None, str] = UNSET
    _default_responsible_team: Union[Unset, None, TeamSummary] = UNSET
    _entry_template_id: Union[Unset, None, str] = UNSET
    _execution_type: Union[Unset, WorkflowTaskSchemaExecutionType] = UNSET
    _prefix: Union[Unset, str] = UNSET
    _status_lifecycle: Union[Unset, WorkflowTaskStatusLifecycle] = UNSET
    _task_group_prefix: Union[Unset, str] = UNSET
    _workflow_output_schema: Union[Unset, None, WorkflowOutputSchema] = UNSET
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
    _type: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append(
            "can_set_assignee_on_task_creation={}".format(repr(self._can_set_assignee_on_task_creation))
        )
        fields.append("default_creation_folder_id={}".format(repr(self._default_creation_folder_id)))
        fields.append(
            "default_entry_execution_folder_id={}".format(repr(self._default_entry_execution_folder_id))
        )
        fields.append("default_responsible_team={}".format(repr(self._default_responsible_team)))
        fields.append("entry_template_id={}".format(repr(self._entry_template_id)))
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append("prefix={}".format(repr(self._prefix)))
        fields.append("status_lifecycle={}".format(repr(self._status_lifecycle)))
        fields.append("task_group_prefix={}".format(repr(self._task_group_prefix)))
        fields.append("workflow_output_schema={}".format(repr(self._workflow_output_schema)))
        fields.append("archive_record={}".format(repr(self._archive_record)))
        fields.append("field_definitions={}".format(repr(self._field_definitions)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskSchema({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        can_set_assignee_on_task_creation = self._can_set_assignee_on_task_creation
        default_creation_folder_id = self._default_creation_folder_id
        default_entry_execution_folder_id = self._default_entry_execution_folder_id
        default_responsible_team: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._default_responsible_team, Unset):
            default_responsible_team = (
                self._default_responsible_team.to_dict() if self._default_responsible_team else None
            )

        entry_template_id = self._entry_template_id
        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

        prefix = self._prefix
        status_lifecycle: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._status_lifecycle, Unset):
            status_lifecycle = self._status_lifecycle.to_dict()

        task_group_prefix = self._task_group_prefix
        workflow_output_schema: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._workflow_output_schema, Unset):
            workflow_output_schema = (
                self._workflow_output_schema.to_dict() if self._workflow_output_schema else None
            )

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
        type = self._type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if can_set_assignee_on_task_creation is not UNSET:
            field_dict["canSetAssigneeOnTaskCreation"] = can_set_assignee_on_task_creation
        if default_creation_folder_id is not UNSET:
            field_dict["defaultCreationFolderId"] = default_creation_folder_id
        if default_entry_execution_folder_id is not UNSET:
            field_dict["defaultEntryExecutionFolderId"] = default_entry_execution_folder_id
        if default_responsible_team is not UNSET:
            field_dict["defaultResponsibleTeam"] = default_responsible_team
        if entry_template_id is not UNSET:
            field_dict["entryTemplateId"] = entry_template_id
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
        if prefix is not UNSET:
            field_dict["prefix"] = prefix
        if status_lifecycle is not UNSET:
            field_dict["statusLifecycle"] = status_lifecycle
        if task_group_prefix is not UNSET:
            field_dict["taskGroupPrefix"] = task_group_prefix
        if workflow_output_schema is not UNSET:
            field_dict["workflowOutputSchema"] = workflow_output_schema
        if archive_record is not UNSET:
            field_dict["archiveRecord"] = archive_record
        if field_definitions is not UNSET:
            field_dict["fieldDefinitions"] = field_definitions
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name
        if type is not UNSET:
            field_dict["type"] = type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_can_set_assignee_on_task_creation() -> Union[Unset, bool]:
            can_set_assignee_on_task_creation = d.pop("canSetAssigneeOnTaskCreation")
            return can_set_assignee_on_task_creation

        can_set_assignee_on_task_creation = (
            get_can_set_assignee_on_task_creation()
            if "canSetAssigneeOnTaskCreation" in d
            else cast(Union[Unset, bool], UNSET)
        )

        def get_default_creation_folder_id() -> Union[Unset, None, str]:
            default_creation_folder_id = d.pop("defaultCreationFolderId")
            return default_creation_folder_id

        default_creation_folder_id = (
            get_default_creation_folder_id()
            if "defaultCreationFolderId" in d
            else cast(Union[Unset, None, str], UNSET)
        )

        def get_default_entry_execution_folder_id() -> Union[Unset, None, str]:
            default_entry_execution_folder_id = d.pop("defaultEntryExecutionFolderId")
            return default_entry_execution_folder_id

        default_entry_execution_folder_id = (
            get_default_entry_execution_folder_id()
            if "defaultEntryExecutionFolderId" in d
            else cast(Union[Unset, None, str], UNSET)
        )

        def get_default_responsible_team() -> Union[Unset, None, TeamSummary]:
            default_responsible_team = None
            _default_responsible_team = d.pop("defaultResponsibleTeam")
            if _default_responsible_team is not None and not isinstance(_default_responsible_team, Unset):
                default_responsible_team = TeamSummary.from_dict(_default_responsible_team)

            return default_responsible_team

        default_responsible_team = (
            get_default_responsible_team()
            if "defaultResponsibleTeam" in d
            else cast(Union[Unset, None, TeamSummary], UNSET)
        )

        def get_entry_template_id() -> Union[Unset, None, str]:
            entry_template_id = d.pop("entryTemplateId")
            return entry_template_id

        entry_template_id = (
            get_entry_template_id() if "entryTemplateId" in d else cast(Union[Unset, None, str], UNSET)
        )

        def get_execution_type() -> Union[Unset, WorkflowTaskSchemaExecutionType]:
            execution_type = None
            _execution_type = d.pop("executionType")
            if _execution_type is not None and _execution_type is not UNSET:
                try:
                    execution_type = WorkflowTaskSchemaExecutionType(_execution_type)
                except ValueError:
                    execution_type = WorkflowTaskSchemaExecutionType.of_unknown(_execution_type)

            return execution_type

        execution_type = (
            get_execution_type()
            if "executionType" in d
            else cast(Union[Unset, WorkflowTaskSchemaExecutionType], UNSET)
        )

        def get_prefix() -> Union[Unset, str]:
            prefix = d.pop("prefix")
            return prefix

        prefix = get_prefix() if "prefix" in d else cast(Union[Unset, str], UNSET)

        def get_status_lifecycle() -> Union[Unset, WorkflowTaskStatusLifecycle]:
            status_lifecycle: Union[Unset, WorkflowTaskStatusLifecycle] = UNSET
            _status_lifecycle = d.pop("statusLifecycle")
            if not isinstance(_status_lifecycle, Unset):
                status_lifecycle = WorkflowTaskStatusLifecycle.from_dict(_status_lifecycle)

            return status_lifecycle

        status_lifecycle = (
            get_status_lifecycle()
            if "statusLifecycle" in d
            else cast(Union[Unset, WorkflowTaskStatusLifecycle], UNSET)
        )

        def get_task_group_prefix() -> Union[Unset, str]:
            task_group_prefix = d.pop("taskGroupPrefix")
            return task_group_prefix

        task_group_prefix = (
            get_task_group_prefix() if "taskGroupPrefix" in d else cast(Union[Unset, str], UNSET)
        )

        def get_workflow_output_schema() -> Union[Unset, None, WorkflowOutputSchema]:
            workflow_output_schema = None
            _workflow_output_schema = d.pop("workflowOutputSchema")
            if _workflow_output_schema is not None and not isinstance(_workflow_output_schema, Unset):
                workflow_output_schema = WorkflowOutputSchema.from_dict(_workflow_output_schema)

            return workflow_output_schema

        workflow_output_schema = (
            get_workflow_output_schema()
            if "workflowOutputSchema" in d
            else cast(Union[Unset, None, WorkflowOutputSchema], UNSET)
        )

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

        def get_type() -> Union[Unset, str]:
            type = d.pop("type")
            return type

        type = get_type() if "type" in d else cast(Union[Unset, str], UNSET)

        workflow_task_schema = cls(
            can_set_assignee_on_task_creation=can_set_assignee_on_task_creation,
            default_creation_folder_id=default_creation_folder_id,
            default_entry_execution_folder_id=default_entry_execution_folder_id,
            default_responsible_team=default_responsible_team,
            entry_template_id=entry_template_id,
            execution_type=execution_type,
            prefix=prefix,
            status_lifecycle=status_lifecycle,
            task_group_prefix=task_group_prefix,
            workflow_output_schema=workflow_output_schema,
            archive_record=archive_record,
            field_definitions=field_definitions,
            id=id,
            name=name,
            type=type,
        )

        workflow_task_schema.additional_properties = d
        return workflow_task_schema

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
    def can_set_assignee_on_task_creation(self) -> bool:
        """ Whether or not tasks of this schema can be created with a non-null assignee. """
        if isinstance(self._can_set_assignee_on_task_creation, Unset):
            raise NotPresentError(self, "can_set_assignee_on_task_creation")
        return self._can_set_assignee_on_task_creation

    @can_set_assignee_on_task_creation.setter
    def can_set_assignee_on_task_creation(self, value: bool) -> None:
        self._can_set_assignee_on_task_creation = value

    @can_set_assignee_on_task_creation.deleter
    def can_set_assignee_on_task_creation(self) -> None:
        self._can_set_assignee_on_task_creation = UNSET

    @property
    def default_creation_folder_id(self) -> Optional[str]:
        """ ID of the default folder for creating workflow task groups """
        if isinstance(self._default_creation_folder_id, Unset):
            raise NotPresentError(self, "default_creation_folder_id")
        return self._default_creation_folder_id

    @default_creation_folder_id.setter
    def default_creation_folder_id(self, value: Optional[str]) -> None:
        self._default_creation_folder_id = value

    @default_creation_folder_id.deleter
    def default_creation_folder_id(self) -> None:
        self._default_creation_folder_id = UNSET

    @property
    def default_entry_execution_folder_id(self) -> Optional[str]:
        """ ID of the default folder for workflow task execution entries """
        if isinstance(self._default_entry_execution_folder_id, Unset):
            raise NotPresentError(self, "default_entry_execution_folder_id")
        return self._default_entry_execution_folder_id

    @default_entry_execution_folder_id.setter
    def default_entry_execution_folder_id(self, value: Optional[str]) -> None:
        self._default_entry_execution_folder_id = value

    @default_entry_execution_folder_id.deleter
    def default_entry_execution_folder_id(self) -> None:
        self._default_entry_execution_folder_id = UNSET

    @property
    def default_responsible_team(self) -> Optional[TeamSummary]:
        if isinstance(self._default_responsible_team, Unset):
            raise NotPresentError(self, "default_responsible_team")
        return self._default_responsible_team

    @default_responsible_team.setter
    def default_responsible_team(self, value: Optional[TeamSummary]) -> None:
        self._default_responsible_team = value

    @default_responsible_team.deleter
    def default_responsible_team(self) -> None:
        self._default_responsible_team = UNSET

    @property
    def entry_template_id(self) -> Optional[str]:
        """ The ID of the template of the entries tasks of this schema will be executed into. """
        if isinstance(self._entry_template_id, Unset):
            raise NotPresentError(self, "entry_template_id")
        return self._entry_template_id

    @entry_template_id.setter
    def entry_template_id(self, value: Optional[str]) -> None:
        self._entry_template_id = value

    @entry_template_id.deleter
    def entry_template_id(self) -> None:
        self._entry_template_id = UNSET

    @property
    def execution_type(self) -> WorkflowTaskSchemaExecutionType:
        """ The method by which instances of this schema are executed """
        if isinstance(self._execution_type, Unset):
            raise NotPresentError(self, "execution_type")
        return self._execution_type

    @execution_type.setter
    def execution_type(self, value: WorkflowTaskSchemaExecutionType) -> None:
        self._execution_type = value

    @execution_type.deleter
    def execution_type(self) -> None:
        self._execution_type = UNSET

    @property
    def prefix(self) -> str:
        """ The prefix for the displayId of tasks of this schema. """
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
    def status_lifecycle(self) -> WorkflowTaskStatusLifecycle:
        if isinstance(self._status_lifecycle, Unset):
            raise NotPresentError(self, "status_lifecycle")
        return self._status_lifecycle

    @status_lifecycle.setter
    def status_lifecycle(self, value: WorkflowTaskStatusLifecycle) -> None:
        self._status_lifecycle = value

    @status_lifecycle.deleter
    def status_lifecycle(self) -> None:
        self._status_lifecycle = UNSET

    @property
    def task_group_prefix(self) -> str:
        """ The prefix for the displayId of task groups containing tasks of this schema """
        if isinstance(self._task_group_prefix, Unset):
            raise NotPresentError(self, "task_group_prefix")
        return self._task_group_prefix

    @task_group_prefix.setter
    def task_group_prefix(self, value: str) -> None:
        self._task_group_prefix = value

    @task_group_prefix.deleter
    def task_group_prefix(self) -> None:
        self._task_group_prefix = UNSET

    @property
    def workflow_output_schema(self) -> Optional[WorkflowOutputSchema]:
        if isinstance(self._workflow_output_schema, Unset):
            raise NotPresentError(self, "workflow_output_schema")
        return self._workflow_output_schema

    @workflow_output_schema.setter
    def workflow_output_schema(self, value: Optional[WorkflowOutputSchema]) -> None:
        self._workflow_output_schema = value

    @workflow_output_schema.deleter
    def workflow_output_schema(self) -> None:
        self._workflow_output_schema = UNSET

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

    @property
    def type(self) -> str:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET
