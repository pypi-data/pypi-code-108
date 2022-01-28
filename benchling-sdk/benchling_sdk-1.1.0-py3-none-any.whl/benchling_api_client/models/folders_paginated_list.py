from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.folder import Folder
from ..types import UNSET, Unset

T = TypeVar("T", bound="FoldersPaginatedList")


@attr.s(auto_attribs=True, repr=False)
class FoldersPaginatedList:
    """  """

    _folders: Union[Unset, List[Folder]] = UNSET
    _next_token: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("folders={}".format(repr(self._folders)))
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "FoldersPaginatedList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folders: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._folders, Unset):
            folders = []
            for folders_item_data in self._folders:
                folders_item = folders_item_data.to_dict()

                folders.append(folders_item)

        next_token = self._next_token

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if folders is not UNSET:
            field_dict["folders"] = folders
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_folders() -> Union[Unset, List[Folder]]:
            folders = []
            _folders = d.pop("folders")
            for folders_item_data in _folders or []:
                folders_item = Folder.from_dict(folders_item_data)

                folders.append(folders_item)

            return folders

        folders = get_folders() if "folders" in d else cast(Union[Unset, List[Folder]], UNSET)

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        folders_paginated_list = cls(
            folders=folders,
            next_token=next_token,
        )

        folders_paginated_list.additional_properties = d
        return folders_paginated_list

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
    def folders(self) -> List[Folder]:
        if isinstance(self._folders, Unset):
            raise NotPresentError(self, "folders")
        return self._folders

    @folders.setter
    def folders(self, value: List[Folder]) -> None:
        self._folders = value

    @folders.deleter
    def folders(self) -> None:
        self._folders = UNSET

    @property
    def next_token(self) -> str:
        if isinstance(self._next_token, Unset):
            raise NotPresentError(self, "next_token")
        return self._next_token

    @next_token.setter
    def next_token(self, value: str) -> None:
        self._next_token = value

    @next_token.deleter
    def next_token(self) -> None:
        self._next_token = UNSET
