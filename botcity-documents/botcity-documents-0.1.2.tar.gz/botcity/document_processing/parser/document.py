from functools import wraps
from typing import Any, Callable, List, Optional, TypeVar, Union, cast

from . import _priv_parser
from .entry import Entry

F = TypeVar('F', bound=Callable[..., Any])


def ensure_parser(func: F) -> F:
    @wraps(func)
    def wrapper(obj, *args, **kwargs):
        if isinstance(obj, DocumentParser):
            if obj._parser is None:
                raise RuntimeError('Please authenticate before trying to run the document parser.')
        else:
            raise NotImplementedError('ensure_parser is only valid for DocumentParser methods.')
        return func(obj, *args, **kwargs)

    return cast(F, wrapper)


class DocumentParser:
    def __init__(self) -> None:
        self._entries = []
        self._parser = None
        self._parser = _priv_parser

    @ensure_parser
    def clear(self):
        """Clear the list of entries.
        """
        self._parser.clear(self)

    @ensure_parser
    def print(self):
        """Print the list of entries.
        """
        for e in self.get_entries():
            print(f"->{e.text} ({e.p1.x}, {e.p1.y} - {e.p4.x}, {e.p4.y})")

    @ensure_parser
    def add_entry(self, entry: Entry):
        """Add an entry into the parser list.

        Args:
            entry (Entry): The entry to be added.
        """
        self._parser.add_entry(self, entry)

    @ensure_parser
    def get_entries(self) -> List[Entry]:
        """The parser entries.

        Returns:
            List[Entry]: The parser entries.
        """
        return self._parser.get_entries(self)

    @ensure_parser
    def set_entries(self, entries: List[Entry]):
        """Sets the list of entries.

        Args:
            entries (List[Entry]): List of entries.
        """
        self._parser.set_entries(self, entries)

    @ensure_parser
    def load_entries(self, entries: List):
        """Load entries into the parser.

        Args:
            entries (List): List of Entry objects or
                List of List containing the required information.
        """
        self._parser.load_entries(self, entries)

    @ensure_parser
    def get_full_text(self) -> str:
        """Returns the full document text.

        Returns:
            str: The document text.
        """
        return self._parser.get_full_text(self)

    @ensure_parser
    def combined_entries(self, *args) -> Entry:
        """Combine a list of entries into a new merged entry.

        Returns:
            Entry: The new merged entry.
        """
        return self._parser.combined_entries(self, *args)

    @ensure_parser
    def get_n_entry(self, text: Optional[str] = "", entry: Optional[Union[int, Entry]] = 0,
                    count: Optional[int] = 1) -> Entry:
        """Get the nth entry corresponding to the parameters.

        Args:
            text (Optional[str], optional): The entry text. Defaults to "".
            entry (Optional[Union[int, Entry]], optional): Reference Entry or index to use as start
                point for the search. Defaults to 0.
            count (Optional[int], optional): Index of search to return. 1 means first entry,
                2 means second entry, etc. Defaults to 1.

        Returns:
            Entry: The corresponding entry.
        """
        return self._parser.get_n_entry(self, text, entry, count)

    @ensure_parser
    def get_first_entry(self, text: Optional[str] = "", entry: Optional[Union[int, Entry]] = 0) -> Entry:
        """Get the first entry which meets the text criteria.

        Args:
            text (Optional[str], optional): The entry text. Defaults to "".
            entry (Optional[Union[int, Entry]], optional): Reference Entry or index to use as start
                point for the search. Defaults to 0.

        Returns:
            Entry: The corresponding entry.
        """
        return self._parser.get_first_entry(self, text, entry)

    @ensure_parser
    def get_second_entry(self, text: Optional[str] = "", entry: Optional[Union[int, Entry]] = 0) -> Entry:
        """get the second entry which meets the text criteria.

        Args:
            text (Optional[str], optional): The entry text. Defaults to "".
            entry (Optional[Union[int, Entry]], optional): Reference Entry or index to use as start
                point for the search. Defaults to 0.

        Returns:
            Entry: The corresponding entry.
        """
        return self._parser.get_second_entry(self, text, entry)

    @ensure_parser
    def get_last_entry(self) -> Entry:
        """Get the last entry on the parser's entry list.

        Returns:
            Entry: The last entry.
        """
        return self._parser.get_last_entry(self)

    @ensure_parser
    def get_first_entry_contains(self, text: Optional[str] = "", entry: Optional[Union[int, Entry]] = 0) -> Entry:
        """Get the first entry which contains the text criteria.

        Args:
            text (Optional[str], optional): The entry partial text. Defaults to "".
            entry (Optional[Union[int, Entry]], optional): Reference Entry or index to use as start
                point for the search. Defaults to 0.

        Returns:
            Entry: The corresponding entry.
        """
        return self._parser.get_first_entry_contains(self, text, entry)

    @ensure_parser
    def read(self, entry: Entry,
             margin_left: float, margin_right: float,
             margin_top: float, margin_bottom: float,
             line_height: Optional[int] = None, data_type=None,
             right_reference: Optional[Entry] = None,
             bottom_reference: Optional[Entry] = None) -> str:
        """Read an area and return its content.

        Args:
            entry (Entry): The anchor entry.
            margin_left (float): Proportion from the anchor's left corner.
            margin_right (float): Proportion from the anchor's right corner.
            margin_top (float): Proportion from the anchor's top.
            margin_bottom (float): Proportion from the anchor's bottom.
            line_height (Optional[int], optional): Line height for compensation. Defaults to None.
            data_type ([type], optional): Expected data type for use with OCR to correct for possible
                reading artifacts. Defaults to None.
            right_reference (Optional[Entry], optional): Reference Entry to use as right
                anchor. Defaults to None.
            bottom_reference (Optional[Entry], optional): Reference Entry to use as bottom
                anchor. Defaults to None.

        Returns:
            str: The text content from the area.
        """
        return self._parser.read(
            self, entry, margin_left, margin_right, margin_top, margin_bottom,
            line_height, data_type, right_reference, bottom_reference
        )
