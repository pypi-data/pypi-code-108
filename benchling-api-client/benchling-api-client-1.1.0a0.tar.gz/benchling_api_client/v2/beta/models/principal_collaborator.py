from typing import Any, cast, Dict, List, Optional, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="PrincipalCollaborator")


@attr.s(auto_attribs=True, repr=False)
class PrincipalCollaborator:
    """  """

    _access_policy_id: str
    _collaborator_id: str
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("access_policy_id={}".format(repr(self._access_policy_id)))
        fields.append("collaborator_id={}".format(repr(self._collaborator_id)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "PrincipalCollaborator({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        access_policy_id = self._access_policy_id
        collaborator_id = self._collaborator_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "accessPolicyId": access_policy_id,
                "collaboratorId": collaborator_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_access_policy_id() -> str:
            access_policy_id = d.pop("accessPolicyId")
            return access_policy_id

        access_policy_id = get_access_policy_id() if "accessPolicyId" in d else cast(str, UNSET)

        def get_collaborator_id() -> str:
            collaborator_id = d.pop("collaboratorId")
            return collaborator_id

        collaborator_id = get_collaborator_id() if "collaboratorId" in d else cast(str, UNSET)

        principal_collaborator = cls(
            access_policy_id=access_policy_id,
            collaborator_id=collaborator_id,
        )

        principal_collaborator.additional_properties = d
        return principal_collaborator

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
    def access_policy_id(self) -> str:
        if isinstance(self._access_policy_id, Unset):
            raise NotPresentError(self, "access_policy_id")
        return self._access_policy_id

    @access_policy_id.setter
    def access_policy_id(self, value: str) -> None:
        self._access_policy_id = value

    @property
    def collaborator_id(self) -> str:
        if isinstance(self._collaborator_id, Unset):
            raise NotPresentError(self, "collaborator_id")
        return self._collaborator_id

    @collaborator_id.setter
    def collaborator_id(self, value: str) -> None:
        self._collaborator_id = value
