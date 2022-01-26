from typing import Any, cast, Dict, List, Optional, Type, TypeVar, Union

import attr

from ..extensions import NotPresentError
from ..models.entry_link import EntryLink
from ..models.entry_table import EntryTable
from ..models.table_note_part_type import TableNotePartType
from ..types import UNSET, Unset

T = TypeVar("T", bound="TableNotePart")


@attr.s(auto_attribs=True, repr=False)
class TableNotePart:
    """ A table with rows and columns of text """

    _links: Union[Unset, List[EntryLink]] = UNSET
    _table: Union[Unset, EntryTable] = UNSET
    _text: Union[Unset, str] = UNSET
    _type: Union[Unset, TableNotePartType] = UNSET
    _indentation: Union[Unset, int] = 0
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def __repr__(self):
        fields = []
        fields.append("links={}".format(repr(self._links)))
        fields.append("table={}".format(repr(self._table)))
        fields.append("text={}".format(repr(self._text)))
        fields.append("type={}".format(repr(self._type)))
        fields.append("indentation={}".format(repr(self._indentation)))
        fields.append("additional_properties={}".format(repr(self.additional_properties)))
        return "TableNotePart({})".format(", ".join(fields))

    def to_dict(self) -> Dict[str, Any]:
        links: Union[Unset, List[Any]] = UNSET
        if not isinstance(self._links, Unset):
            links = []
            for links_item_data in self._links:
                links_item = links_item_data.to_dict()

                links.append(links_item)

        table: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self._table, Unset):
            table = self._table.to_dict()

        text = self._text
        type: Union[Unset, int] = UNSET
        if not isinstance(self._type, Unset):
            type = self._type.value

        indentation = self._indentation

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if links is not UNSET:
            field_dict["links"] = links
        if table is not UNSET:
            field_dict["table"] = table
        if text is not UNSET:
            field_dict["text"] = text
        if type is not UNSET:
            field_dict["type"] = type
        if indentation is not UNSET:
            field_dict["indentation"] = indentation

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()

        def get_links() -> Union[Unset, List[EntryLink]]:
            links = []
            _links = d.pop("links")
            for links_item_data in _links or []:
                links_item = EntryLink.from_dict(links_item_data)

                links.append(links_item)

            return links

        links = get_links() if "links" in d else cast(Union[Unset, List[EntryLink]], UNSET)

        def get_table() -> Union[Unset, EntryTable]:
            table: Union[Unset, EntryTable] = UNSET
            _table = d.pop("table")
            if not isinstance(_table, Unset):
                table = EntryTable.from_dict(_table)

            return table

        table = get_table() if "table" in d else cast(Union[Unset, EntryTable], UNSET)

        def get_text() -> Union[Unset, str]:
            text = d.pop("text")
            return text

        text = get_text() if "text" in d else cast(Union[Unset, str], UNSET)

        def get_type() -> Union[Unset, TableNotePartType]:
            type = None
            _type = d.pop("type")
            if _type is not None and _type is not UNSET:
                try:
                    type = TableNotePartType(_type)
                except ValueError:
                    type = TableNotePartType.of_unknown(_type)

            return type

        type = get_type() if "type" in d else cast(Union[Unset, TableNotePartType], UNSET)

        def get_indentation() -> Union[Unset, int]:
            indentation = d.pop("indentation")
            return indentation

        indentation = get_indentation() if "indentation" in d else cast(Union[Unset, int], UNSET)

        table_note_part = cls(
            links=links,
            table=table,
            text=text,
            type=type,
            indentation=indentation,
        )

        table_note_part.additional_properties = d
        return table_note_part

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
    def links(self) -> List[EntryLink]:
        """Array of links referenced in the caption via an @-mention, hyperlink, or the drag-n-dropped preview attached to the note."""
        if isinstance(self._links, Unset):
            raise NotPresentError(self, "links")
        return self._links

    @links.setter
    def links(self, value: List[EntryLink]) -> None:
        self._links = value

    @links.deleter
    def links(self) -> None:
        self._links = UNSET

    @property
    def table(self) -> EntryTable:
        """Actual tabular data with rows and columns of text on the note."""
        if isinstance(self._table, Unset):
            raise NotPresentError(self, "table")
        return self._table

    @table.setter
    def table(self, value: EntryTable) -> None:
        self._table = value

    @table.deleter
    def table(self) -> None:
        self._table = UNSET

    @property
    def text(self) -> str:
        """ The caption of the table. """
        if isinstance(self._text, Unset):
            raise NotPresentError(self, "text")
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value

    @text.deleter
    def text(self) -> None:
        self._text = UNSET

    @property
    def type(self) -> TableNotePartType:
        if isinstance(self._type, Unset):
            raise NotPresentError(self, "type")
        return self._type

    @type.setter
    def type(self, value: TableNotePartType) -> None:
        self._type = value

    @type.deleter
    def type(self) -> None:
        self._type = UNSET

    @property
    def indentation(self) -> int:
        """All notes have an indentation level - the default is 0 for no indent. For lists, indentation gives notes hierarchy - a bulleted list with children is modeled as one note part with indentation 1 followed by note parts with indentation 2, for example."""
        if isinstance(self._indentation, Unset):
            raise NotPresentError(self, "indentation")
        return self._indentation

    @indentation.setter
    def indentation(self, value: int) -> None:
        self._indentation = value

    @indentation.deleter
    def indentation(self) -> None:
        self._indentation = UNSET
