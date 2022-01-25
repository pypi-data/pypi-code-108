from typing import Any, cast, Dict, List, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.plate import Plate
from ..models.plate_worklist_items_list_type import PlateWorklistItemsListType
from ..types import UNSET, Unset

T = TypeVar("T", bound="PlateWorklistItemsList")


@attr.s(auto_attribs=True, repr=False)
class PlateWorklistItemsList:
    """  """

    _next_token: Union[Unset, str] = UNSET
    _type: Union[Unset, PlateWorklistItemsListType] = UNSET
    _worklist_items: Union[Unset, List[Plate]] = UNSET

    def __repr__(self):
        fields = []
        fields.append("next_token={}".format(repr(self._next_token)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("worklist_items={}".format(repr(self._worklist_items)))
        return "PlateWorklistItemsList({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        next_token = self._next_token
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        worklist_items: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._worklist_items, Unset):
            worklist_items = []
            for worklist_items_item_data in self._worklist_items:
                worklist_items_item = worklist_items_item_data.to_dict()

                worklist_items.append(worklist_items_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update({})
        if next_token is not UNSET:
            field_dict["nextToken"] = next_token
        if type is not UNSET:
            field_dict["type"] = type
        if worklist_items is not UNSET:
            field_dict["worklistItems"] = worklist_items

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_next_token() -> Union[Unset, str]:
            next_token = d.pop("nextToken")
            return next_token

        next_token = get_next_token() if "nextToken" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, PlateWorklistItemsListType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = PlateWorklistItemsListType(_type)
                except ValueError:
                    type = PlateWorklistItemsListType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, PlateWorklistItemsListType], UNSET)

        def get_worklist_items() -> Union[Unset, List[Plate]]:
            worklist_items = []
            _worklist_items = d.pop("worklistItems")
            for worklist_items_item_data in _worklist_items or []:
                worklist_items_item = Plate.from_dict(worklist_items_item_data)

                worklist_items.append(worklist_items_item)

            return worklist_items

        worklist_items = (
            get_worklist_items() if "worklistItems" in d else cast(Union[Unset, List[Plate]], UNSET)
        )

        plate_worklist_items_list = cls(
            next_token=next_token,
            type=type,
            worklist_items=worklist_items,
        )

        return plate_worklist_items_list

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

    @property
    def type(self) -> PlateWorklistItemsListType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: PlateWorklistItemsListType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def worklist_items(self) -> List[Plate]:
        if isinstance(self._worklist_items, Unset):
            raise NotPresentError(self, "worklist_items")
        return self._worklist_items

    @worklist_items.setter
    def worklist_items(self, value: List[Plate]) -> None:
        self._worklist_items = value

    @worklist_items.deleter
    def worklist_items(self) -> None:
        self._worklist_items = UNSET
