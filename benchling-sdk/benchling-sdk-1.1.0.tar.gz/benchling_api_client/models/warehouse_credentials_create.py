from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WarehouseCredentialsCreate")


@attr.s(auto_attribs=True, repr=False)
class WarehouseCredentialsCreate:
    """  """

    _expires_in: int

    def __repr__(self):
        fields = []
        fields.append("expires_in={}".format(repr(self._expires_in)))
        return "WarehouseCredentialsCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        expires_in = self._expires_in

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "expiresIn": expires_in,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_expires_in() -> int:
            expires_in = d.pop("expiresIn")
            return expires_in

        expires_in = get_expires_in() if "expiresIn" in d else cast(int, UNSET)

        warehouse_credentials_create = cls(
            expires_in=expires_in,
        )

        return warehouse_credentials_create

    @property
    def expires_in(self) -> int:
        """Duration, in seconds, that credentials should be active for. Must be greater than 0 and less than 3600."""
        if isinstance(self._expires_in, Unset):
            raise NotPresentError(self, "expires_in")
        return self._expires_in

    @expires_in.setter
    def expires_in(self, value: int) -> None:
        self._expires_in = value
