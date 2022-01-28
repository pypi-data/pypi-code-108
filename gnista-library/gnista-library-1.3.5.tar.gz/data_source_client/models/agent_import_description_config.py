from typing import Any, Dict, List, Type, TypeVar, Union

import attr

from ..types import UNSET, Unset

T = TypeVar("T", bound="AgentImportDescriptionConfig")


@attr.s(auto_attribs=True)
class AgentImportDescriptionConfig:
    """ """

    discriminator: str
    agent_type: Union[Unset, None, str] = UNSET
    connection_string: Union[Unset, None, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        discriminator = self.discriminator
        agent_type = self.agent_type
        connection_string = self.connection_string

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "discriminator": discriminator,
            }
        )
        if agent_type is not UNSET:
            field_dict["agentType"] = agent_type
        if connection_string is not UNSET:
            field_dict["connectionString"] = connection_string

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        discriminator = d.pop("discriminator")

        agent_type = d.pop("agentType", UNSET)

        connection_string = d.pop("connectionString", UNSET)

        agent_import_description_config = cls(
            discriminator=discriminator,
            agent_type=agent_type,
            connection_string=connection_string,
        )

        agent_import_description_config.additional_properties = d
        return agent_import_description_config

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
