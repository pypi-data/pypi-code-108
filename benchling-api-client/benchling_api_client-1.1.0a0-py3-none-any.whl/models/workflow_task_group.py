from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.folder import Folder
from ..models.team_summary import TeamSummary
from ..models.user_summary import UserSummary
from ..models.workflow_output_summary import WorkflowOutputSummary
from ..models.workflow_task_group_execution_type import WorkflowTaskGroupExecutionType
from ..models.workflow_task_schema_summary import WorkflowTaskSchemaSummary
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroup")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroup:
    """  """

    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _creator: Union[Unset, UserSummary] = UNSET
    _execution_type: Union[Unset, WorkflowTaskGroupExecutionType] = UNSET
    _folder: Union[Unset, Folder] = UNSET
    _outputs: Union[Unset, List[WorkflowOutputSummary]] = UNSET
    _responsible_team: Union[Unset, None, TeamSummary] = UNSET
    _tasks: Union[Unset, List[WorkflowTaskSummary]] = UNSET
    _watchers: Union[Unset, List[UserSummary]] = UNSET
    _web_url: Union[Unset, str] = UNSET
    _workflow_task_schema: Union[Unset, WorkflowTaskSchemaSummary] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("creator={}".format(repr(self._creator)))
        fields.append("execution_type={}".format(repr(self._execution_type)))
        fields.append("folder={}".format(repr(self._folder)))
        fields.append("outputs={}".format(repr(self._outputs)))
        fields.append("responsible_team={}".format(repr(self._responsible_team)))
        fields.append("tasks={}".format(repr(self._tasks)))
        fields.append("watchers={}".format(repr(self._watchers)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("workflow_task_schema={}".format(repr(self._workflow_task_schema)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroup({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        creator: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creator, Unset):
            creator = self._creator.to_dict()

        execution_type: Union[Unset, int] = UNSET
        if not isinstance(self._execution_type, Unset):
            execution_type = self._execution_type.value

        folder: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._folder, Unset):
            folder = self._folder.to_dict()

        outputs: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._outputs, Unset):
            outputs = []
            for outputs_item_data in self._outputs:
                outputs_item = outputs_item_data.to_dict()

                outputs.append(outputs_item)

        responsible_team: Union[Unset, None, Dict[str, Any]] = UNSET
        if not isinstance(self._responsible_team, Unset):
            responsible_team = self._responsible_team.to_dict() if self._responsible_team else None

        tasks: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._tasks, Unset):
            tasks = []
            for tasks_item_data in self._tasks:
                tasks_item = tasks_item_data.to_dict()

                tasks.append(tasks_item)

        watchers: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._watchers, Unset):
            watchers = []
            for watchers_item_data in self._watchers:
                watchers_item = watchers_item_data.to_dict()

                watchers.append(watchers_item)

        web_url = self._web_url
        workflow_task_schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._workflow_task_schema, Unset):
            workflow_task_schema = self._workflow_task_schema.to_dict()

        display_id = self._display_id
        id = self._id
        name = self._name

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if creator is not UNSET:
            field_dict["creator"] = creator
        if execution_type is not UNSET:
            field_dict["executionType"] = execution_type
        if folder is not UNSET:
            field_dict["folder"] = folder
        if outputs is not UNSET:
            field_dict["outputs"] = outputs
        if responsible_team is not UNSET:
            field_dict["responsibleTeam"] = responsible_team
        if tasks is not UNSET:
            field_dict["tasks"] = tasks
        if watchers is not UNSET:
            field_dict["watchers"] = watchers
        if web_url is not UNSET:
            field_dict["webURL"] = web_url
        if workflow_task_schema is not UNSET:
            field_dict["workflowTaskSchema"] = workflow_task_schema
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if id is not UNSET:
            field_dict["id"] = id
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_creation_origin() -> Union[Unset, CreationOrigin]:
            creation_origin: Union[Unset, CreationOrigin] = UNSET
            _creation_origin = d.pop("creationOrigin")
            if not isinstance(_creation_origin, Unset):
                creation_origin = CreationOrigin.from_dict(_creation_origin)

            return creation_origin

        creation_origin = (
            get_creation_origin() if "creationOrigin" in d else cast(Union[Unset, CreationOrigin], UNSET)
        )

        def get_creator() -> Union[Unset, UserSummary]:
            creator: Union[Unset, UserSummary] = UNSET
            _creator = d.pop("creator")
            if not isinstance(_creator, Unset):
                creator = UserSummary.from_dict(_creator)

            return creator

        creator = get_creator() if "creator" in d else cast(Union[Unset, UserSummary], UNSET)

        def get_execution_type() -> Union[Unset, WorkflowTaskGroupExecutionType]:
            execution_type = None
            _execution_type = d.pop("executionType")
            if _execution_type is not None and _execution_type is not UNSET:
                try:
                    execution_type = WorkflowTaskGroupExecutionType(_execution_type)
                except ValueError:
                    execution_type = WorkflowTaskGroupExecutionType.of_unknown(_execution_type)

            return execution_type

        execution_type = (
            get_execution_type()
            if "executionType" in d
            else cast(Union[Unset, WorkflowTaskGroupExecutionType], UNSET)
        )

        def get_folder() -> Union[Unset, Folder]:
            folder: Union[Unset, Folder] = UNSET
            _folder = d.pop("folder")
            if not isinstance(_folder, Unset):
                folder = Folder.from_dict(_folder)

            return folder

        folder = get_folder() if "folder" in d else cast(Union[Unset, Folder], UNSET)

        def get_outputs() -> Union[Unset, List[WorkflowOutputSummary]]:
            outputs = []
            _outputs = d.pop("outputs")
            for outputs_item_data in _outputs or []:
                outputs_item = WorkflowOutputSummary.from_dict(outputs_item_data)

                outputs.append(outputs_item)

            return outputs

        outputs = get_outputs() if "outputs" in d else cast(Union[Unset, List[WorkflowOutputSummary]], UNSET)

        def get_responsible_team() -> Union[Unset, None, TeamSummary]:
            responsible_team = None
            _responsible_team = d.pop("responsibleTeam")
            if _responsible_team is not None and not isinstance(_responsible_team, Unset):
                responsible_team = TeamSummary.from_dict(_responsible_team)

            return responsible_team

        responsible_team = (
            get_responsible_team() if "responsibleTeam" in d else cast(Union[Unset, None, TeamSummary], UNSET)
        )

        def get_tasks() -> Union[Unset, List[WorkflowTaskSummary]]:
            tasks = []
            _tasks = d.pop("tasks")
            for tasks_item_data in _tasks or []:
                tasks_item = WorkflowTaskSummary.from_dict(tasks_item_data)

                tasks.append(tasks_item)

            return tasks

        tasks = get_tasks() if "tasks" in d else cast(Union[Unset, List[WorkflowTaskSummary]], UNSET)

        def get_watchers() -> Union[Unset, List[UserSummary]]:
            watchers = []
            _watchers = d.pop("watchers")
            for watchers_item_data in _watchers or []:
                watchers_item = UserSummary.from_dict(watchers_item_data)

                watchers.append(watchers_item)

            return watchers

        watchers = get_watchers() if "watchers" in d else cast(Union[Unset, List[UserSummary]], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_task_schema() -> Union[Unset, WorkflowTaskSchemaSummary]:
            workflow_task_schema: Union[Unset, WorkflowTaskSchemaSummary] = UNSET
            _workflow_task_schema = d.pop("workflowTaskSchema")
            if not isinstance(_workflow_task_schema, Unset):
                workflow_task_schema = WorkflowTaskSchemaSummary.from_dict(_workflow_task_schema)

            return workflow_task_schema

        workflow_task_schema = (
            get_workflow_task_schema()
            if "workflowTaskSchema" in d
            else cast(Union[Unset, WorkflowTaskSchemaSummary], UNSET)
        )

        def get_display_id() -> Union[Unset, str]:
            display_id = d.pop("displayId")
            return display_id

        display_id = get_display_id() if "displayId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        workflow_task_group = cls(
            creation_origin=creation_origin,
            creator=creator,
            execution_type=execution_type,
            folder=folder,
            outputs=outputs,
            responsible_team=responsible_team,
            tasks=tasks,
            watchers=watchers,
            web_url=web_url,
            workflow_task_schema=workflow_task_schema,
            display_id=display_id,
            id=id,
            name=name,
        )

        workflow_task_group.additional_properties = d
        return workflow_task_group

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
    def creation_origin(self) -> CreationOrigin:
        if isinstance(self._creation_origin, Unset):
            raise NotPresentError(self, "creation_origin")
        return self._creation_origin

    @creation_origin.setter
    def creation_origin(self, value: CreationOrigin) -> None:
        self._creation_origin = value

    @creation_origin.deleter
    def creation_origin(self) -> None:
        self._creation_origin = UNSET

    @property
    def creator(self) -> UserSummary:
        if isinstance(self._creator, Unset):
            raise NotPresentError(self, "creator")
        return self._creator

    @creator.setter
    def creator(self, value: UserSummary) -> None:
        self._creator = value

    @creator.deleter
    def creator(self) -> None:
        self._creator = UNSET

    @property
    def execution_type(self) -> WorkflowTaskGroupExecutionType:
        """ The method by which the workflow is executed """
        if isinstance(self._execution_type, Unset):
            raise NotPresentError(self, "execution_type")
        return self._execution_type

    @execution_type.setter
    def execution_type(self, value: WorkflowTaskGroupExecutionType) -> None:
        self._execution_type = value

    @execution_type.deleter
    def execution_type(self) -> None:
        self._execution_type = UNSET

    @property
    def folder(self) -> Folder:
        if isinstance(self._folder, Unset):
            raise NotPresentError(self, "folder")
        return self._folder

    @folder.setter
    def folder(self, value: Folder) -> None:
        self._folder = value

    @folder.deleter
    def folder(self) -> None:
        self._folder = UNSET

    @property
    def outputs(self) -> List[WorkflowOutputSummary]:
        """ The outputs of the workflow task group """
        if isinstance(self._outputs, Unset):
            raise NotPresentError(self, "outputs")
        return self._outputs

    @outputs.setter
    def outputs(self, value: List[WorkflowOutputSummary]) -> None:
        self._outputs = value

    @outputs.deleter
    def outputs(self) -> None:
        self._outputs = UNSET

    @property
    def responsible_team(self) -> Optional[TeamSummary]:
        if isinstance(self._responsible_team, Unset):
            raise NotPresentError(self, "responsible_team")
        return self._responsible_team

    @responsible_team.setter
    def responsible_team(self, value: Optional[TeamSummary]) -> None:
        self._responsible_team = value

    @responsible_team.deleter
    def responsible_team(self) -> None:
        self._responsible_team = UNSET

    @property
    def tasks(self) -> List[WorkflowTaskSummary]:
        """ The input tasks to the workflow task group """
        if isinstance(self._tasks, Unset):
            raise NotPresentError(self, "tasks")
        return self._tasks

    @tasks.setter
    def tasks(self, value: List[WorkflowTaskSummary]) -> None:
        self._tasks = value

    @tasks.deleter
    def tasks(self) -> None:
        self._tasks = UNSET

    @property
    def watchers(self) -> List[UserSummary]:
        """ The users watching the workflow task group """
        if isinstance(self._watchers, Unset):
            raise NotPresentError(self, "watchers")
        return self._watchers

    @watchers.setter
    def watchers(self, value: List[UserSummary]) -> None:
        self._watchers = value

    @watchers.deleter
    def watchers(self) -> None:
        self._watchers = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the workflow task group """
        if isinstance(self._web_url, Unset):
            raise NotPresentError(self, "web_url")
        return self._web_url

    @web_url.setter
    def web_url(self, value: str) -> None:
        self._web_url = value

    @web_url.deleter
    def web_url(self) -> None:
        self._web_url = UNSET

    @property
    def workflow_task_schema(self) -> WorkflowTaskSchemaSummary:
        if isinstance(self._workflow_task_schema, Unset):
            raise NotPresentError(self, "workflow_task_schema")
        return self._workflow_task_schema

    @workflow_task_schema.setter
    def workflow_task_schema(self, value: WorkflowTaskSchemaSummary) -> None:
        self._workflow_task_schema = value

    @workflow_task_schema.deleter
    def workflow_task_schema(self) -> None:
        self._workflow_task_schema = UNSET

    @property
    def display_id(self) -> str:
        """ User-friendly ID of the workflow task group """
        if isinstance(self._display_id, Unset):
            raise NotPresentError(self, "display_id")
        return self._display_id

    @display_id.setter
    def display_id(self, value: str) -> None:
        self._display_id = value

    @display_id.deleter
    def display_id(self) -> None:
        self._display_id = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow task group """
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
        """ The name of the workflow task group """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET
