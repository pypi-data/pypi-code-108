from typing import Any, cast, Dict, Type, TypeVar

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="FolderCreate")


@attr.s(auto_attribs=True, repr=False)
class FolderCreate:
    """  """

    _name: str
    _parent_folder_id: str

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("parent_folder_id={}".format(repr(self._parent_folder_id)))
        return "FolderCreate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        parent_folder_id = self._parent_folder_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                "name": name,
                "parentFolderId": parent_folder_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> str:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(str, UNSET)

        def get_parent_folder_id() -> str:
            parent_folder_id = d.pop("parentFolderId")
            return parent_folder_id

        parent_folder_id = get_parent_folder_id() if "parentFolderId" in d else cast(str, UNSET)

        folder_create = cls(
            name=name,
            parent_folder_id=parent_folder_id,
        )

        return folder_create

    @property
    def name(self) -> str:
        """ The name of the new folder. """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def parent_folder_id(self) -> str:
        """ The ID of the parent folder. """
        if isinstance(self._parent_folder_id, Unset):
            raise NotPresentError(self, "parent_folder_id")
        return self._parent_folder_id

    @parent_folder_id.setter
    def parent_folder_id(self, value: str) -> None:
        self._parent_folder_id = value
