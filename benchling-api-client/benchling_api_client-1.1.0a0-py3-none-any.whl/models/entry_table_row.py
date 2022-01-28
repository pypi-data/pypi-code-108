from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_table_cell import EntryTableCell
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryTableRow")


@attr.s(auto_attribs=True, repr=False)
class EntryTableRow:
    """ Each has property 'cells' that is an array of cell objects """

    _cells: Union[Unset, List[EntryTableCell]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("cells={}".format(repr(self._cells)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryTableRow({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        cells: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._cells, Unset):
            cells = []
            for cells_item_data in self._cells:
                cells_item = cells_item_data.to_dict()

                cells.append(cells_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cells is not UNSET:
            field_dict["cells"] = cells

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_cells() -> Union[Unset, List[EntryTableCell]]:
            cells = []
            _cells = d.pop("cells")
            for cells_item_data in _cells or []:
                cells_item = EntryTableCell.from_dict(cells_item_data)

                cells.append(cells_item)

            return cells

        cells = get_cells() if "cells" in d else cast(Union[Unset, List[EntryTableCell]], UNSET)

        entry_table_row = cls(
            cells=cells,
        )

        entry_table_row.additional_properties = d
        return entry_table_row

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
    def cells(self) -> List[EntryTableCell]:
        if isinstance(self._cells, Unset):
            raise NotPresentError(self, "cells")
        return self._cells

    @cells.setter
    def cells(self, value: List[EntryTableCell]) -> None:
        self._cells = value

    @cells.deleter
    def cells(self) -> None:
        self._cells = UNSET
