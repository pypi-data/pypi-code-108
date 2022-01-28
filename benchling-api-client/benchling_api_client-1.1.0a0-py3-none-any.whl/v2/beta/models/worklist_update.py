from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..types import UNSET, Unset

T = TypeVar("T", bound="WorklistUpdate")


@attr.s(auto_attribs=True, repr=False)
class WorklistUpdate:
    """  """

    _name: Union[Unset, str] = UNSET
    _worklist_item_ids: Union[Unset, List[str]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("name={}".format(repr(self._name)))
        fields.append("worklist_item_ids={}".format(repr(self._worklist_item_ids)))
        return "WorklistUpdate({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        name = self._name
        worklist_item_ids: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklist_item_ids, Unset):
            worklist_item_ids = self._worklist_item_ids

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if worklist_item_ids is not UNSET:
            field_dict["worklistItemIds"] = worklist_item_ids

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_worklist_item_ids() -> Union[Unset, List[str]]:
            worklist_item_ids = cast(List[str], d.pop("worklistItemIds"))

            return worklist_item_ids

        worklist_item_ids = (
            get_worklist_item_ids() if "worklistItemIds" in d else cast(Union[Unset, List[str]], UNSET)
        )

        worklist_update = cls(
            name=name,
            worklist_item_ids=worklist_item_ids,
        )

        return worklist_update

    @property
    def name(self) -> str:
        """ Name of the worklist """
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
    def worklist_item_ids(self) -> List[str]:
        """An ordered set of IDs to assign as worklist items. IDs should reference existing items which fit the worklist's specific type. For instance, a worklist of type container should only have item IDs which represent containers.
        Replaces any existing worklist items with this set.
        """
        if isinstance(self._worklist_item_ids, Unset):
            raise NotPresentError(self, "worklist_item_ids")
        return self._worklist_item_ids

    @worklist_item_ids.setter
    def worklist_item_ids(self, value: List[str]) -> None:
        self._worklist_item_ids = value

    @worklist_item_ids.deleter
    def worklist_item_ids(self) -> None:
        self._worklist_item_ids = UNSET
