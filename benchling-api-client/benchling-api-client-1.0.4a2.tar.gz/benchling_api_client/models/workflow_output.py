from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.creation_origin import CreationOrigin
from ..models.fields import Fields
from ..models.workflow_task_group_summary import WorkflowTaskGroupSummary
from ..models.workflow_task_summary import WorkflowTaskSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutput")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutput:
    """  """

    _creation_origin: Union[Unset, CreationOrigin] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    _task: Union[Unset, WorkflowTaskSummary] = UNSET
    _web_url: Union[Unset, str] = UNSET
    _workflow_task_group: Union[Unset, WorkflowTaskGroupSummary] = UNSET
    _display_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("creation_origin={}".format(repr(self._creation_origin)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("task={}".format(repr(self._task)))
        fields.append("web_url={}".format(repr(self._web_url)))
        fields.append("workflow_task_group={}".format(repr(self._workflow_task_group)))
        fields.append("display_id={}".format(repr(self._display_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutput({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        creation_origin: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._creation_origin, Unset):
            creation_origin = self._creation_origin.to_dict()

        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        task: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._task, Unset):
            task = self._task.to_dict()

        web_url = self._web_url
        workflow_task_group: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._workflow_task_group, Unset):
            workflow_task_group = self._workflow_task_group.to_dict()

        display_id = self._display_id
        id = self._id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if creation_origin is not UNSET:
            field_dict["creationOrigin"] = creation_origin
        if fields is not UNSET:
            field_dict["fields"] = fields
        if task is not UNSET:
            field_dict["task"] = task
        if web_url is not UNSET:
            field_dict["webURL"] = web_url
        if workflow_task_group is not UNSET:
            field_dict["workflowTaskGroup"] = workflow_task_group
        if display_id is not UNSET:
            field_dict["displayId"] = display_id
        if id is not UNSET:
            field_dict["id"] = id

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

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        def get_task() -> Union[Unset, WorkflowTaskSummary]:
            task: Union[Unset, WorkflowTaskSummary] = UNSET
            _task = d.pop("task")
            if not isinstance(_task, Unset):
                task = WorkflowTaskSummary.from_dict(_task)

            return task

        task = get_task() if "task" in d else cast(Union[Unset, WorkflowTaskSummary], UNSET)

        def get_web_url() -> Union[Unset, str]:
            web_url = d.pop("webURL")
            return web_url

        web_url = get_web_url() if "webURL" in d else cast(Union[Unset, str], UNSET)

        def get_workflow_task_group() -> Union[Unset, WorkflowTaskGroupSummary]:
            workflow_task_group: Union[Unset, WorkflowTaskGroupSummary] = UNSET
            _workflow_task_group = d.pop("workflowTaskGroup")
            if not isinstance(_workflow_task_group, Unset):
                workflow_task_group = WorkflowTaskGroupSummary.from_dict(_workflow_task_group)

            return workflow_task_group

        workflow_task_group = (
            get_workflow_task_group()
            if "workflowTaskGroup" in d
            else cast(Union[Unset, WorkflowTaskGroupSummary], UNSET)
        )

        def get_display_id() -> Union[Unset, str]:
            display_id = d.pop("displayId")
            return display_id

        display_id = get_display_id() if "displayId" in d else cast(Union[Unset, str], UNSET)

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        workflow_output = cls(
            creation_origin=creation_origin,
            fields=fields,
            task=task,
            web_url=web_url,
            workflow_task_group=workflow_task_group,
            display_id=display_id,
            id=id,
        )

        workflow_output.additional_properties = d
        return workflow_output

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
    def task(self) -> WorkflowTaskSummary:
        if isinstance(self._task, Unset):
            raise NotPresentError(self, "task")
        return self._task

    @task.setter
    def task(self, value: WorkflowTaskSummary) -> None:
        self._task = value

    @task.deleter
    def task(self) -> None:
        self._task = UNSET

    @property
    def web_url(self) -> str:
        """ URL of the workflow output """
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
    def workflow_task_group(self) -> WorkflowTaskGroupSummary:
        if isinstance(self._workflow_task_group, Unset):
            raise NotPresentError(self, "workflow_task_group")
        return self._workflow_task_group

    @workflow_task_group.setter
    def workflow_task_group(self, value: WorkflowTaskGroupSummary) -> None:
        self._workflow_task_group = value

    @workflow_task_group.deleter
    def workflow_task_group(self) -> None:
        self._workflow_task_group = UNSET

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
        """ The ID of the workflow output """
        if isinstance(self._id, Unset):
            raise NotPresentError(self, "id")
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        self._id = value

    @id.deleter
    def id(self) -> None:
        self._id = UNSET
