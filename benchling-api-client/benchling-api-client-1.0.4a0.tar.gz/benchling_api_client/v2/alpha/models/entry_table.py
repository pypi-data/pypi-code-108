from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_table_row import EntryTableRow
from ..types import UNSET, Unset

T = TypeVar("T", bound="EntryTable")


@attr.s(auto_attribs=True, repr=False)
class EntryTable:
    """Actual tabular data with rows and columns of text on the note."""

    _column_labels: Union[Unset, List[Optional[str]]] = UNSET
    _name: Union[Unset, str] = UNSET
    _rows: Union[Unset, List[EntryTableRow]] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("column_labels={}".format(repr(self._column_labels)))
        fields.append("name={}".format(repr(self._name)))
        fields.append("rows={}".format(repr(self._rows)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "EntryTable({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        column_labels: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._column_labels, Unset):
            column_labels = self._column_labels

        name = self._name
        rows: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._rows, Unset):
            rows = []
            for rows_item_data in self._rows:
                rows_item = rows_item_data.to_dict()

                rows.append(rows_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if column_labels is not UNSET:
            field_dict["columnLabels"] = column_labels
        if name is not UNSET:
            field_dict["name"] = name
        if rows is not UNSET:
            field_dict["rows"] = rows

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_column_labels() -> Union[Unset, List[Optional[str]]]:
            column_labels = cast(List[Optional[str]], d.pop("columnLabels"))

            return column_labels

        column_labels = (
            get_column_labels() if "columnLabels" in d else cast(Union[Unset, List[Optional[str]]], UNSET)
        )

        def get_name() -> Union[Unset, str]:
            name = d.pop("name")
            return name

        name = get_name() if "name" in d else cast(Union[Unset, str], UNSET)

        def get_rows() -> Union[Unset, List[EntryTableRow]]:
            rows = []
            _rows = d.pop("rows")
            for rows_item_data in _rows or []:
                rows_item = EntryTableRow.from_dict(rows_item_data)

                rows.append(rows_item)

            return rows

        rows = get_rows() if "rows" in d else cast(Union[Unset, List[EntryTableRow]], UNSET)

        entry_table = cls(
            column_labels=column_labels,
            name=name,
            rows=rows,
        )

        entry_table.additional_properties = d
        return entry_table

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
    def column_labels(self) -> List[Optional[str]]:
        """Array of strings, with one item per column. Defaults to null, if the user is using the default, but is set if the user has given a custom name to the column."""
        if isinstance(self._column_labels, Unset):
            raise NotPresentError(self, "column_labels")
        return self._column_labels

    @column_labels.setter
    def column_labels(self, value: List[Optional[str]]) -> None:
        self._column_labels = value

    @column_labels.deleter
    def column_labels(self) -> None:
        self._column_labels = UNSET

    @property
    def name(self) -> str:
        """Name of the table - defaults to e.g. Table1 but can be renamed."""
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
    def rows(self) -> List[EntryTableRow]:
        """ Array of row objects. """
        if isinstance(self._rows, Unset):
            raise NotPresentError(self, "rows")
        return self._rows

    @rows.setter
    def rows(self, value: List[EntryTableRow]) -> None:
        self._rows = value

    @rows.deleter
    def rows(self) -> None:
        self._rows = UNSET
