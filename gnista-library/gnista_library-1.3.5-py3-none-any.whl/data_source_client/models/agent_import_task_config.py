from typing import Any, Dict, List, Type, TypeVar, Union, cast

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentImportTaskConfig")


@attr.s(auto_attribs=True)
class AgentImportTaskConfig:
    """ """

    discriminator: str
    name: Union[Unset, None, str] = UNSET
    tags: Union[Unset, None, List[str]] = UNSET
    connection_string: Union[Unset, None, str] = UNSET
    agent_type: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        name = self.name
        tags: Union[Unset, None, List[str]] = UNSET
        if not isinstance(self.tags, Unset):
            if self.tags is None:
                tags = None
            else:
                tags = self.tags

        connection_string = self.connection_string
        agent_type = self.agent_type

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if name is not UNSET:
            field_dict["name"] = name
        if tags is not UNSET:
            field_dict["tags"] = tags
        if connection_string is not UNSET:
            field_dict["connectionString"] = connection_string
        if agent_type is not UNSET:
            field_dict["agentType"] = agent_type

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        name = d.pop("name", UNSET)

        tags = cast(List[str], d.pop("tags", UNSET))

        connection_string = d.pop("connectionString", UNSET)

        agent_type = d.pop("agentType", UNSET)

        agent_import_task_config = cls(
            discriminator=discriminator,
            name=name,
            tags=tags,
            connection_string=connection_string,
            agent_type=agent_type,
        )

        agent_import_task_config.additional_properties = d
        return agent_import_task_config

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
