from typing import Any, Dict, NewType
from abc import ABC
from dataclasses import dataclass
from datetime import date
from daybook.domain.services import get_valid_date

Reader = NewType("ReaderName", str)
BookID = NewType("BookID", int)
BookTitle = NewType("BookTitle", str)
BookSubtitle = NewType("BookSubtitle", str)
Author = NewType("Author", str)


class AbstractDomainEntity(ABC):
    entity_id: Any
    entity_type: Any

    def set_entity_props(self, entity_id: Any, entity_type: Any):
        self.entity_id = entity_id
        self.entity_type = entity_type

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, self.entity_type):
            return False
        return __o.entity_id == self.entity_id

    def __hash__(self) -> int:
        return hash(self.entity_id)

    def __gt__(self, __o: object) -> bool:
        if not isinstance(__o, self.entity_type):
            return False
        if self.entity_id is None:
            return False
        if __o.entity_id is None:
            return True
        return self.entity_id > __o.entity_id


@dataclass
class Book:
    author: Author
    title: BookTitle
    subtitle: BookSubtitle
    key: int = None

    def __hash__(self) -> int:
        return hash((self.author, self.title, self.subtitle, self.key))


@dataclass
class PageRange:
    start: int
    end: int

    def __hash__(self) -> int:
        return hash((self.start, self.end))


class ReadingLogEntry:
    id: int
    date: date
    reader: Reader
    book: Book
    pages: PageRange

    def __init__(
        self,
        entry_id: int,
        entry_date: date,
        reader: Reader,
        book: Book,
        pages: PageRange,
    ) -> None:
        self.id = entry_id
        self.date = entry_date
        self.reader = reader
        self.book = book
        self.pages = pages

    def __eq__(self, __o: object) -> bool:
        return (
            self.date == __o.date and self.reader == __o.reader and self.book == __o.book and self.pages == __o.pages
        )

    def __hash__(self) -> int:
        return hash((self.date, self.reader, self.book, self.pages))


def get_valid_pages(pages: PageRange, latest_page: int) -> PageRange:
    if not pages.end:
        raise Exception("Missing required end page")
    if not pages.start:
        if latest_page < pages.end:
            pages.start = latest_page
        else:
            raise Exception("End page precedes last page read")
    if pages.start >= pages.end:
        raise Exception("Start page must precede end page")
    return pages


class ReadingLog(AbstractDomainEntity):
    def __init__(
        self, reader: Reader, id: int = None, entries: Dict[int, ReadingLogEntry] = None
    ) -> None:
        self.reader = reader
        self.entries = entries if entries else dict()
        self.events = []
        self.set_entity_props(self.reader, ReadingLog)
        self.available_books = []
        self.id = id

    def add_available_book(self, b: Book):
        if b:
            self.available_books.append(b)

    def update_reader(self, updated_reader: Reader):
        self.reader = updated_reader
        for entry_id in self.entries:
            entry = self.entries.get(entry_id)
            if entry:
                entry.reader = self.reader

    def get_lastest_page_read_for_book(self, book: Book):
        latest_page_read = 0
        for curr_entry_id in self.entries:
            entry = self.entries.get(curr_entry_id)
            if entry.book.key == book.key:
                if entry.pages.end > latest_page_read:
                    latest_page_read = entry.pages.end
        return latest_page_read

    def add_entry(
        self, entry_date: date, book: Book, pages: PageRange, entry_id: int = None
    ) -> ReadingLogEntry:
        entry_date = get_valid_date(entry_date)
        latest_page = self.get_lastest_page_read_for_book(book)
        valid_pages = get_valid_pages(pages, latest_page)
        self.entries[entry_id] = ReadingLogEntry(
            entry_id, entry_date, self.reader, book, valid_pages
        )
        return self.entries[entry_id]

    def add_entry_using_book_key(
        self, entry_date: date, book_key: int, pages: PageRange
    ) -> ReadingLogEntry:
        entry_date = get_valid_date(entry_date)
        book = None
        for available_book in self.available_books:
            if available_book.key == book_key:
                book = available_book
                break
        if book is None:
            raise Exception("book key not found")
        latest_page = self.get_lastest_page_read_for_book(book)
        valid_pages = get_valid_pages(pages, latest_page)
        self.entries[-1] = ReadingLogEntry(
            -1, entry_date, self.reader, book, valid_pages
        )
        return self.entries[-1]

    def delete_entry(self, entry_id: int) -> ReadingLogEntry:
        deleted_entry = None
        updated_entries = dict()
        for curr_entry_id in self.entries:
            entry = self.entries[curr_entry_id]
            if entry.id == entry_id:
                deleted_entry = entry
            else:
                updated_entries[entry.id] = entry
        self.entries = updated_entries
        return deleted_entry

    def update_entry(
        self,
        entry_id: int,
        entry_date: date,
        book: Book,
        pages: PageRange,
    ) -> ReadingLogEntry:
        updated_entry = None
        entry_date = get_valid_date(entry_date)
        latest_page = self.get_lastest_page_read_for_book(book)
        valid_pages = get_valid_pages(pages, latest_page)
        updated_entries = dict()
        for curr_entry_id in self.entries:
            entry = self.entries[curr_entry_id]
            if entry.id == entry_id:
                updated_entry = ReadingLogEntry(
                    entry_id, entry_date, self.reader, book, valid_pages
                )
                updated_entries[updated_entry.id] = updated_entry
            else:
                updated_entries[entry.id] = entry
        self.entries = updated_entries
        return updated_entry

    def update_book(self, book: Book) -> Book:
        updated_book = None
        updated_entries = dict()
        for curr_entry_id in self.entries:
            entry = self.entries[curr_entry_id]
            if entry.book.key == book.key:
                if not updated_book:
                    updated_book = entry.book
                entry.book = book
            updated_entries[entry.id] = entry
        self.entries = updated_entries
        return updated_book
