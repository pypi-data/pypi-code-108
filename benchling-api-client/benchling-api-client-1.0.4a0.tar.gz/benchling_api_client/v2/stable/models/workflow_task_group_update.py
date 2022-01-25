from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorkflowTaskGroupUpdate")


@attr.s(auto_attribs=True, repr=False)
class WorkflowTaskGroupUpdate:
    """  """

    _folder_id: Union[Unset, str] = UNSET
    _name: Union[Unset, str] = UNSET
    _watcher_ids: Union[Unset, List[str]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("folder_id={}".format(repr(self._folder_id)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("watcher_ids={}".format(repr(self._watcher_ids)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "WorkflowTaskGroupUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        folder_id = self._folder_id
        name = self._name
        watcher_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._watcher_ids, Unset):
            watcher_ids = self._watcher_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if folder_id is not UNSET:
            field_dict["folderId"] = folder_id
        if name is not UNSET:
            field_dict["name"] = name
        if watcher_ids is not UNSET:
            field_dict["watcherIds"] = watcher_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_folder_id() -> Union[Unset, str]:
            folder_id = d.pop("folderId")
            return folder_id

        folder_id = get_folder_id() if "folderId" in d else cast(Union[Unset, str], UNSET)

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_watcher_ids() -> Union[Unset, List[str]]:
            watcher_ids = cast(List[str], d.pop("watcherIds"))

            return watcher_ids

        watcher_ids = get_watcher_ids() if "watcherIds" in d else cast(Union[Unset, List[str]], UNSET)

        workflow_task_group_update = cls(
            folder_id=folder_id,
            name=name,
            watcher_ids=watcher_ids,
        )

        workflow_task_group_update.additional_properties = d
        return workflow_task_group_update

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
    def folder_id(self) -> str:
        """ ID of the folder that contains the workflow task group """
        if isinstance(self._folder_id, Unset):
            raise NotPresentError(self, "folder_id")
        return self._folder_id

    @folder_id.setter
    def folder_id(self, value: str) -> None:
        self._folder_id = value

    @folder_id.deleter
    def folder_id(self) -> None:
        self._folder_id = UNSET

    @property
    def name(self) -> str:
        """ The name of the workflow task group """
        if isinstance(self._name, Unset):
            raise NotPresentError(self, "name")
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @name.deleter
    def name(self) -> None:
        self._name = UNSET

    @property
    def watcher_ids(self) -> List[str]:
        """ IDs of the users watching the workflow task group """
        if isinstance(self._watcher_ids, Unset):
            raise NotPresentError(self, "watcher_ids")
        return self._watcher_ids

    @watcher_ids.setter
    def watcher_ids(self, value: List[str]) -> None:
        self._watcher_ids = value

    @watcher_ids.deleter
    def watcher_ids(self) -> None:
        self._watcher_ids = UNSET
