from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.workflow_task_schema_summary import WorkflowTaskSchemaSummary
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowFlowchartNodeConfig")


@attr.s(auto_attribs=True, repr=False)
class WorkflowFlowchartNodeConfig:
    """  """

    _id: Union[Unset, str] = UNSET
    _task_schema: Union[Unset, WorkflowTaskSchemaSummary] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("id={}".format(repr(self._id)))
        fields.append("task_schema={}".format(repr(self._task_schema)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowFlowchartNodeConfig({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        id = self._id
        task_schema: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._task_schema, Unset):
            task_schema = self._task_schema.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if task_schema is not UNSET:
            field_dict["taskSchema"] = task_schema

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_task_schema() -> Union[Unset, WorkflowTaskSchemaSummary]:
            task_schema: Union[Unset, WorkflowTaskSchemaSummary] = UNSET
            _task_schema = d.pop("taskSchema")
            if not isinstance(_task_schema, Unset):
                task_schema = WorkflowTaskSchemaSummary.from_dict(_task_schema)

            return task_schema

        task_schema = (
            get_task_schema() if "taskSchema" in d else cast(Union[Unset, WorkflowTaskSchemaSummary], UNSET)
        )

        workflow_flowchart_node_config = cls(
            id=id,
            task_schema=task_schema,
        )

        workflow_flowchart_node_config.additional_properties = d
        return workflow_flowchart_node_config

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
        """ The ID of the workflow flowchart node config """
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
    def task_schema(self) -> WorkflowTaskSchemaSummary:
        if isinstance(self._task_schema, Unset):
            raise NotPresentError(self, "task_schema")
        return self._task_schema

    @task_schema.setter
    def task_schema(self, value: WorkflowTaskSchemaSummary) -> None:
        self._task_schema = value

    @task_schema.deleter
    def task_schema(self) -> None:
        self._task_schema = UNSET
