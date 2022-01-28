from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowFlowchartEdgeConfig")


@attr.s(auto_attribs=True, repr=False)
class WorkflowFlowchartEdgeConfig:
    """  """

    _from_node_config_id: Union[Unset, str] = UNSET
    _id: Union[Unset, str] = UNSET
    _to_node_config_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("from_node_config_id={}".format(repr(self._from_node_config_id)))
        fields.append("id={}".format(repr(self._id)))
        fields.append("to_node_config_id={}".format(repr(self._to_node_config_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowFlowchartEdgeConfig({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        from_node_config_id = self._from_node_config_id
        id = self._id
        to_node_config_id = self._to_node_config_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if from_node_config_id is not UNSET:
            field_dict["fromNodeConfigId"] = from_node_config_id
        if id is not UNSET:
            field_dict["id"] = id
        if to_node_config_id is not UNSET:
            field_dict["toNodeConfigId"] = to_node_config_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_from_node_config_id() -> Union[Unset, str]:
            from_node_config_id = d.pop("fromNodeConfigId")
            return from_node_config_id

        from_node_config_id = (
            get_from_node_config_id() if "fromNodeConfigId" in d else cast(Union[Unset, str], UNSET)
        )

        def get_id() -> Union[Unset, str]:
            id = d.pop("id")
            return id

        id = get_id() if "id" in d else cast(Union[Unset, str], UNSET)

        def get_to_node_config_id() -> Union[Unset, str]:
            to_node_config_id = d.pop("toNodeConfigId")
            return to_node_config_id

        to_node_config_id = (
            get_to_node_config_id() if "toNodeConfigId" in d else cast(Union[Unset, str], UNSET)
        )

        workflow_flowchart_edge_config = cls(
            from_node_config_id=from_node_config_id,
            id=id,
            to_node_config_id=to_node_config_id,
        )

        workflow_flowchart_edge_config.additional_properties = d
        return workflow_flowchart_edge_config

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
    def from_node_config_id(self) -> str:
        """ The ID of the source workflow flowchart node config of this edge """
        if isinstance(self._from_node_config_id, Unset):
            raise NotPresentError(self, "from_node_config_id")
        return self._from_node_config_id

    @from_node_config_id.setter
    def from_node_config_id(self, value: str) -> None:
        self._from_node_config_id = value

    @from_node_config_id.deleter
    def from_node_config_id(self) -> None:
        self._from_node_config_id = UNSET

    @property
    def id(self) -> str:
        """ The ID of the workflow flowchart edge config """
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
    def to_node_config_id(self) -> str:
        """ The ID of the destination workflow flowchart node config of this edge """
        if isinstance(self._to_node_config_id, Unset):
            raise NotPresentError(self, "to_node_config_id")
        return self._to_node_config_id

    @to_node_config_id.setter
    def to_node_config_id(self, value: str) -> None:
        self._to_node_config_id = value

    @to_node_config_id.deleter
    def to_node_config_id(self) -> None:
        self._to_node_config_id = UNSET
