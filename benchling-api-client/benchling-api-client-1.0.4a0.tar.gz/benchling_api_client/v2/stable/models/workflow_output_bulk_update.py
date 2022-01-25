from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.fields import Fields
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowOutputBulkUpdate")


@attr.s(auto_attribs=True, repr=False)
class WorkflowOutputBulkUpdate:
    """  """

    _workflow_output_id: Union[Unset, str] = UNSET
    _fields: Union[Unset, Fields] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("workflow_output_id={}".format(repr(self._workflow_output_id)))
        fields.append("fields={}".format(repr(self._fields)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowOutputBulkUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        workflow_output_id = self._workflow_output_id
        fields: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._fields, Unset):
            fields = self._fields.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if workflow_output_id is not UNSET:
            field_dict["workflowOutputId"] = workflow_output_id
        if fields is not UNSET:
            field_dict["fields"] = fields

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_workflow_output_id() -> Union[Unset, str]:
            workflow_output_id = d.pop("workflowOutputId")
            return workflow_output_id

        workflow_output_id = (
            get_workflow_output_id() if "workflowOutputId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_fields() -> Union[Unset, Fields]:
            fields: Union[Unset, Fields] = UNSET
            _fields = d.pop("fields")
            if not isinstance(_fields, Unset):
                fields = Fields.from_dict(_fields)

            return fields

        fields = get_fields() if "fields" in d else cast(Union[Unset, Fields], UNSET)

        workflow_output_bulk_update = cls(
            workflow_output_id=workflow_output_id,
            fields=fields,
        )

        workflow_output_bulk_update.additional_properties = d
        return workflow_output_bulk_update

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
    def workflow_output_id(self) -> str:
        """ The ID of the workflow output """
        if isinstance(self._workflow_output_id, Unset):
            raise NotPresentError(self, "workflow_output_id")
        return self._workflow_output_id

    @workflow_output_id.setter
    def workflow_output_id(self, value: str) -> None:
        self._workflow_output_id = value

    @workflow_output_id.deleter
    def workflow_output_id(self) -> None:
        self._workflow_output_id = UNSET

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
