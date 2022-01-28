from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.team_summary import TeamSummary
from ..models.workflow_task_schema_execution_type import WorkflowTaskSchemaExecutionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskSchema")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskSchema:
    """  """

    _execution_type: Union[Unset, WorkflowTaskSchemaExecutionType] = UNSET
    _can_set_assignee_on_task_creation: Union[Unset, bool] = UNSET
    _default_creation_folder_id: Union[Unset, None, str] = UNSET
    _default_entry_execution_folder_id: Union[Unset, None, str] = UNSET
    _default_responsible_team: Union[Unset, None, TeamSummary] = UNSET
    _entry_template_id: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append(
            "can_set_assignee_on_task_creation={}".format(repr(self._can_set_assignee_on_task_creation))
        )
        fields.append("default_creation_folder_id={}".format(repr(self._default_creation_folder_id)))
        fields.append(
            "default_entry_execution_folder_id={}".format(repr(self._default_entry_execution_folder_id))
        )
        fields.append("default_responsible_team={}".format(repr(self._default_responsible_team)))
        fields.append("entry_template_id={}".format(repr(self._entry_template_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskSchema({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

        can_set_assignee_on_task_creation = self._can_set_assignee_on_task_creation
        default_creation_folder_id = self._default_creation_folder_id
        default_entry_execution_folder_id = self._default_entry_execution_folder_id
        default_responsible_team: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._default_responsible_team, Unset):
            default_responsible_team = (
                self._default_responsible_team.to_dict() if self._default_responsible_team else None
            )

        entry_template_id = self._entry_template_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
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

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

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

        workflow_task_schema = cls(
            execution_type=execution_type,
            can_set_assignee_on_task_creation=can_set_assignee_on_task_creation,
            default_creation_folder_id=default_creation_folder_id,
            default_entry_execution_folder_id=default_entry_execution_folder_id,
            default_responsible_team=default_responsible_team,
            entry_template_id=entry_template_id,
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
